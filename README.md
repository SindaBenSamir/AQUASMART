# Prédiction des Précipitations

Ce projet permet de prédire les précipitations journalières et saisonnières à Tunis à partir de données météorologiques historiques et en temps réel.

## 📁 Structure du projet

- `historique.py` : Récupère les données historiques via l'API Meteostat.
- `temps_réel.py` : Récupère les données météo en temps réel.
- `insert_api.py` : Insère les données météo dans une base de données MySQL pour affichage dans Power BI.
- `insert_apijournalière.py` : Insère les données journalières dans une base de données MySQL
- `prediction.py` : Prédiction journalière des précipitations.
- `prediction_saiso.py` : Prédiction saisonnière (saison sèche, moyenne ou pluvieuse).
- `main_predictor.py` : Lance automatiquement la récupération des données + prédiction.
- `season_api.py` : Prédit la saison à partir des données récupérées via l’API.

## ⚙️ Installation

1. **Créer un environnement virtuel**

```bash
python -m venv venv
```bash
venv\Scripts\activate


