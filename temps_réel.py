# temps_reel.py
from meteostat import Hourly, Stations
from datetime import datetime, timedelta
import pandas as pd

# Trouver la station météo la plus proche de Tunis
stations = Stations()
stations = stations.nearby(36.8065, 10.1815)  # Coordonnées de Tunis
stations = stations.fetch()

# Vérifier si une station a été trouvée
if not stations.empty:
    station_id = stations.index[0]  # Prendre l'ID de la première station trouvée
    print(f"📍 Station sélectionnée : {station_id}")
else:
    print("❌ Aucune station trouvée, essaie une autre localisation.")
    exit()

# Définir la période (dernière heure)
end = datetime.utcnow()
start = end - timedelta(hours=1)

# Récupérer les données horaires pour la station sélectionnée
data = Hourly(station_id, start, end)
data = data.fetch()

# Sauvegarder les données dans un fichier CSV
data.to_csv('precipitations_tunis_realtime.csv')

print("📊 Données météo actuelles sauvegardées dans 'precipitations_tunis_realtime.csv'")
