import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from math import sqrt
from datetime import datetime
import pickle

# Charger les données historiques
historical_path = 'precipitations_combined.csv'
data = pd.read_csv(historical_path)

# Harmoniser les colonnes avec l'API Meteostat
column_mapping = {
    'temp': 'tavg',  # temp = température moyenne
    'dwpt': 'tmin',  # dwpt = point de rosée (approximation pour tmin)
    'rhum': 'tmax',  # rhum = humidité relative (approximation pour tmax)
}
data.rename(columns=column_mapping, inplace=True)

# Remplacer les valeurs manquantes
for col in ['prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']:
    if col in data.columns:
        data[col] = data[col].fillna(0)

# Séparer les features et la cible
X = data[['tavg', 'tmin', 'tmax', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']]
y = data['prcp']

# Entraîner le modèle
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Charger les données en temps réel
realtime_path = 'precipitations_tunis_realtime.csv'
data_realtime = pd.read_csv(realtime_path)

# Renommer et harmoniser les colonnes
if 'temp' in data_realtime.columns:
    data_realtime.rename(columns=column_mapping, inplace=True)

def add_missing_columns(df, reference_df):
    missing_cols = set(reference_df.columns) - set(df.columns)
    for col in missing_cols:
        df[col] = 0
    return df

data_realtime = add_missing_columns(data_realtime, X)

# Réordonner les colonnes
data_realtime = data_realtime[X.columns]

# Remplacer les NaN restants
for col in X.columns:
    data_realtime[col] = data_realtime[col].fillna(data[col].median())

# Faire une prédiction
predictions = model.predict(data_realtime)

# Enregistrer les prédictions dans un fichier CSV
today = datetime.today().strftime('%Y-%m-%d')
result_df = pd.DataFrame({'Date': [today], 'Précipitation_Prévue': [predictions[0]]})

file_path = "predictions_journalieres.csv"
try:
    existing_data = pd.read_csv(file_path, sep=";")
    result_df = pd.concat([existing_data, result_df], ignore_index=True)
except FileNotFoundError:
    pass

result_df.to_csv(file_path, index=False, sep=";")
print("✅ Prédiction ajoutée à 'predictions_journalieres.csv'")

# Sauvegarder le modèle
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)