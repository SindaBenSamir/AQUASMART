import pulp
import random
from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpStatus

# Données du problème
secteurs = ["agriculture", "industrie", "domestique"]
besoins = {
    "agriculture": random.randint(10, 80),
    "industrie": random.randint(10, 80),
    "domestique": random.randint(10, 80)
}

# Générer des priorités aléatoires (entre 1 et 3)
priorites = {
    "agriculture": random.randint(1, 3),
    "industrie": random.randint(1, 3),
    "domestique": random.randint(1, 3)
}
capacite_max_vanne = 100  # Capacité maximale de chaque vanne (m³/h)
pertes_eau = 5  # Pertes d'eau estimées par vanne (m³/h)
perte_max_pourcentage = 0.1  # Pertes d'eau maximales autorisées (10% des débits totaux)

# Nouveaux paramètres
niveau_eau_barrage = 80  # Niveau d'eau du barrage en pourcentage (0-100)
precipitations_prevues = 20  # Précipitations prévues en mm
saison = "sécheresse"  # ou "pluies"

# Ajustements basés sur les nouveaux paramètres
capacite_max_vanne_ajustee = capacite_max_vanne * (niveau_eau_barrage / 100)
pertes_eau_ajustees = pertes_eau - (precipitations_prevues * 0.05)

if saison == "sécheresse":
    besoins["agriculture"] *= 1.2
elif saison == "pluies":
    besoins["domestique"] *= 0.9

# Création du problème d'optimisation
prob = pulp.LpProblem("Optimisation_Eau_Deux_Vannes", pulp.LpMaximize)

# Variables de décision
ouverture_vanne1 = pulp.LpVariable("ouverture_vanne1", lowBound=0, upBound=1)  # Degré d'ouverture de la vanne 1
ouverture_vanne2 = pulp.LpVariable("ouverture_vanne2", lowBound=0, upBound=1)  # Degré d'ouverture de la vanne 2
debits = {s: pulp.LpVariable(f"debit_{s}", lowBound=0, upBound=besoins[s]) for s in secteurs}

# Fonction objectif
# Maximiser l'efficacité de l'eau tout en minimisant les pertes des deux vannes
prob += pulp.lpSum([priorites[s] * debits[s] for s in secteurs]) - pertes_eau_ajustees * (ouverture_vanne1 + ouverture_vanne2), "Efficacite_Eau"

# Contraintes existantes
# 1. La somme des débits ne doit pas dépasser la capacité totale des deux vannes
prob += pulp.lpSum([debits[s] for s in secteurs]) <= capacite_max_vanne_ajustee * (ouverture_vanne1 + ouverture_vanne2), "Capacite_Vannes_Ajustee"

# 2. Les débits ne doivent pas dépasser les besoins de chaque secteur
for s in secteurs:
    prob += debits[s] <= besoins[s], f"Besoins_{s}_Ajustes"

# 3. Les vannes ne doivent pas être ouvertes si aucun secteur n'a besoin d'eau
prob += pulp.lpSum([debits[s] for s in secteurs]) >= 0.1 * (ouverture_vanne1 + ouverture_vanne2), "Vannes_Ouvertes_Si_Besoin"

# Nouvelles contraintes
# 4. Contrainte de débit minimal pour les secteurs prioritaires
for s in secteurs:
    prob += debits[s] >= 0.2 * besoins[s] * (ouverture_vanne1 + ouverture_vanne2), f"Debit_Minimal_{s}"

# 5. Contrainte de pertes d'eau maximales
prob += pertes_eau_ajustees * (ouverture_vanne1 + ouverture_vanne2) <= perte_max_pourcentage * pulp.lpSum([debits[s] for s in secteurs]), "Pertes_Maximales_Ajustees"

# 6. Contrainte de partage équitable : aucun secteur ne doit dépasser 40% de la capacité totale
for s in secteurs:
    prob += debits[s] <= 0.4 * capacite_max_vanne_ajustee * (ouverture_vanne1 + ouverture_vanne2), f"Partage_Equitable_{s}"

# Résolution du problème
prob.solve()

# Affichage des résultats
print("Statut de la solution:", pulp.LpStatus[prob.status])
print("Degré d'ouverture de la vanne 1 (0 = fermée, 1 = entièrement ouverte):", pulp.value(ouverture_vanne1))
print("Degré d'ouverture de la vanne 2 (0 = fermée, 1 = entièrement ouverte):", pulp.value(ouverture_vanne2))
print("Débits optimaux par secteur:")
for s in secteurs: 
    print(f"{s}: {pulp.value(debits[s])} m³/h")
print("Pertes d'eau totales:", pulp.value(pertes_eau_ajustees * (ouverture_vanne1 + ouverture_vanne2)))