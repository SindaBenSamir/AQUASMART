import pandas as pd

# Charger les deux datasets
data_tunis = pd.read_csv('precipitations_tunis.csv')
data_lyon = pd.read_csv('precipitations_lyon.csv')

# Afficher les premières lignes pour vérifier la structure
print("Données Tunis:")
print(data_tunis.head())

print("\nDonnées Lyon:")
print(data_lyon.head())

# Harmoniser les noms de colonnes si nécessaire
column_mapping_tunis = {
    'temp': 'tavg',  # temp = température moyenne
    'dwpt': 'tmin',  # dwpt = point de rosée (approximation pour tmin)
    'rhum': 'tmax',  # rhum = humidité relative (approximation pour tmax)
}
column_mapping_lyon = {
    'temperature': 'tavg',  # ajustez selon les noms réels des colonnes
    'dew_point': 'tmin',
    'humidity': 'tmax',
}

# Appliquer les changements de noms de colonnes
data_tunis.rename(columns=column_mapping_tunis, inplace=True)
data_lyon.rename(columns=column_mapping_lyon, inplace=True)

# Assurez-vous que les colonnes sont compatibles
common_columns = ['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']

# Ajouter des colonnes manquantes dans l'un des datasets, si nécessaire
for col in common_columns:
    if col not in data_tunis.columns:
        data_tunis[col] = 0
    if col not in data_lyon.columns:
        data_lyon[col] = 0

# Concaténer les deux datasets verticalement
combined_data = pd.concat([data_tunis, data_lyon], ignore_index=True)

# Afficher les premières lignes du dataset combiné
print("\nDonnées combinées :")
print(combined_data.head())

# Sauvegarder le fichier combiné
combined_data.to_csv('precipitations_combined.csv', index=False)
