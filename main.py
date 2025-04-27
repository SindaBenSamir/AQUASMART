from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import pulp
from pulp import LpProblem, LpVariable, LpMaximize, LpStatus, lpSum
from datetime import datetime
import csv
import os
import httpx

app = FastAPI()

class OptimisationInput(BaseModel):
    niveau_eau_barrage: float  # entre 0 et 100
    besoins: Dict[str, float]  # besoins par secteur
    priorites: Dict[str, int]  # priorités par secteur (1 à 3)

def lire_derniere_precipitation(chemin_csv: str) -> float:
    """Lit la dernière valeur de précipitations prévues depuis un CSV au format ;"""
    try:
        with open(chemin_csv, mode="r", encoding="utf-8") as fichier_csv:
            reader = csv.DictReader(fichier_csv, delimiter=";")
            lignes = list(reader)
            if not lignes:
                raise ValueError("Le fichier météo est vide.")
            derniere_ligne = lignes[-1]
            return float(derniere_ligne.get("Précipitation_Prévue", 0.0))
    except Exception as e:
        raise ValueError(f"Erreur lors de la lecture des précipitations : {str(e)}")

@app.post("/optimisation")
def optimiser_eau(data: OptimisationInput):
    secteurs = list(data.besoins.keys())

    capacite_max_vanne = 100

    # 🔵 Lire la dernière précipitation prévue dans predictions_journalieres.csv
    try:
        precipitations_prevues = lire_derniere_precipitation("C:/Users/user/Documents/Pcd/predictions_journalieres.csv")
    except Exception as e:
        return {"erreur": str(e)}

    # 🔵 Appel API pour obtenir la saison prédite
    try:
        response = httpx.get("http://127.0.0.1:8000/prediction_saisonniere")
        if response.status_code == 200:
            saison_predite = response.json()["prediction"]
        else:
            return {"erreur": "Impossible d'obtenir la saison prédite."}
    except Exception as e:
        return {"erreur": f"Erreur lors de l'appel à l'API de prédiction: {str(e)}"}

    # 🔵 Ajustements en fonction du niveau d'eau
    capacite_disponible = capacite_max_vanne * (data.niveau_eau_barrage / 100)

    besoins = data.besoins.copy()

    # 🔵 Ajustement des besoins selon la saison prédite
    if saison_predite == "seche":
        if "agriculture" in besoins:
            besoins["agriculture"] *= 1.2
    elif saison_predite == "pluvieuse":
        if "industrie" in besoins:
            besoins["industrie"] *= 0.9
    elif saison_predite == "moyenne":
        if "industrie" in besoins:
            besoins["industrie"] *= 0.5
            besoins["industrie"] *= 0.5    

    # 🔵 Création du problème d'optimisation
    prob = LpProblem("Optimisation_Eau_Sans_Pertes", LpMaximize)

    # Débit alloué à chaque secteur
    debits = {s: LpVariable(f"debit_{s}", lowBound=0, upBound=besoins[s]) for s in secteurs}

    # Fonction objectif : maximiser la somme pondérée des débits
    prob += lpSum((data.priorites[s] * debits[s]) for s in secteurs)

    # 🔵 CONTRAINTES
    reserve_minimale = 0.3  # 30% de réserve
    capacite_maximale_utilisable = capacite_disponible * (1 - reserve_minimale)

    # La somme des débits doit être inférieure à la capacité utilisable
    prob += lpSum([debits[s] for s in secteurs]) <= capacite_maximale_utilisable

    # Chaque secteur reçoit au moins 20% de ses besoins
    for s in secteurs:
        prob += debits[s] >= 0.2 * besoins[s]

    # 🔵 Résolution
    prob.solve()

    result = {
        "statut": LpStatus[prob.status],
        "capacite_utilisee": round(sum(pulp.value(debits[s]) for s in secteurs), 2),
        "saison_predite": saison_predite,
        "precipitations_prevues": precipitations_prevues,
        "debits": {s: round(pulp.value(debits[s]), 2) for s in secteurs}
    }

    # 🔵 Historique CSV
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    ligne = {
        "date": now,
        "capacite_utilisee": result["capacite_utilisee"],
        "saison_predite": saison_predite,
        "precipitations_prevues": precipitations_prevues
    }

    for secteur in secteurs:
        ligne[f"debit_{secteur}"] = result["debits"][secteur]

    chemin_fichier = "historique_optimisation.csv"
    fichier_existe = os.path.exists(chemin_fichier)

    with open(chemin_fichier, mode="a", newline="", encoding="utf-8") as fichier_csv:
        writer = csv.DictWriter(fichier_csv, fieldnames=ligne.keys())
        if not fichier_existe:
            writer.writeheader()
        writer.writerow(ligne)

    return result
