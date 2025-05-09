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
- `season_api.py` : Rend l'API de la prédiction saisonniére.

## ⚙️ Installation

1. **Créer un environnement virtuel**
```bash
python -m venv venv
2. **Activer l’environnement virtuel**
   ```bash
venv\Scripts\activate


## 💧 Détection d’anomalies (via Autoencoder GRU)

### 📂 Dataset
- Les données utilisées sont traitées et enrichies avec des variables temporelles (jour, heure, saison…).
- Ce dataset est ensuite utilisé pour entraîner un **modèle GRU autoencodeur** afin de détecter des anomalies dans le comportement des capteurs.

### 🧠 Entraînement
- Le modèle est entraîné localement, puis sauvegardé dans un fichier :  
  `autoencoder_model.h5`


---

## ⚙️ 2. Optimisation de l’utilisation de l’eau

### 🔌 Entrée (via Raspberry Pi)
- Le Raspberry Pi génère un fichier **JSON** , qui est la collecte de données des capteurs de niveaux, contenant :
  - Le **niveau d’eau actuel** du barrage
  - Les **besoins en eau** de chaque secteur (agriculture, industrie…)
  - Les **priorités** associées à chaque secteur

Ce fichier est envoyé via une **requête POST** à l’API locale.

### 📈 Optimisation
- L’algorithme d’optimisation traite la requête JSON.
- Il génère un **fichier CSV** contenant les quantités d’eau allouées à chaque secteur et les décisions d’ouverture ou fermeture des **vannes**.

### 🔁 Sortie (vers Raspberry & Arduino)
- Le CSV généré est **envoyé au Raspberry Pi**, qui transmet les instructions aux **vannes via Arduino**.
- L’Arduino contrôle physiquement les **vannes ** en fonction des ordres reçus.



