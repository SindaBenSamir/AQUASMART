from meteostat import Daily, Stations
from datetime import datetime
import pandas as pd

# Définir la période d'étude
start = datetime(2016, 1, 1)
end = datetime(2025, 4, 12)


# Trouver la station météo la plus proche de Tunis
stations = Stations()
stations = stations.nearby(36.8065, 10.1815)  # Coordonnées de Tunis
station = stations.fetch(1)  # Prendre la station la plus proche
station_id = station.index[0]

print(f"📍 Station sélectionnée : {station_id}")

# Récupérer les données journalières
data = Daily(station_id, start, end)
data = data.fetch()

# Afficher les premières lignes
print(data.head())

# Enregistrer en CSV
data.to_csv("precipitations_tunis.csv")
print("✅ Données enregistrées dans 'precipitations_tunis.csv'")
