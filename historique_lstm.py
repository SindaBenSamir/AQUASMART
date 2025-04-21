from meteostat import Daily, Stations
from datetime import datetime
import pandas as pd

# Définir la période d'étude
start = datetime(2016, 1, 1)
end = datetime(2023, 12, 31)

# Coordonnées de Lyon, France
stations = Stations()
stations = stations.nearby(45.76, 4.84)  # Coordonnées de Lyon
station = stations.fetch(1)  # Prendre la station la plus proche
station_id = station.index[0]

print(f"📍 Station sélectionnée : {station_id}")

# Récupérer les données journalières
data = Daily(station_id, start, end)
data = data.fetch()

# Afficher les premières lignes
print(data.head())

# Enregistrer en CSV
data.to_csv("precipitations_lyon.csv")
print("✅ Données enregistrées dans 'precipitations_lyon.csv'")
