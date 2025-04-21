from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf

# Charger le modèle et le scaler
model = tf.keras.models.load_model("season_lstm_model.h5")
scaler = joblib.load("scaler.pkl")

# Colonnes utilisées
features = ['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']

app = FastAPI()

class PredictionResult(BaseModel):
    prediction: str

@app.get("/")
def read_root():
    return {"message": "API de prédiction saisonnière opérationnelle 🌦️"}

@app.get("/prediction_saisonniere", response_model=PredictionResult)
def predict_saison():
    try:
        # Charger les données
        df = pd.read_csv("precipitations_tunis.csv")
        df = df.sort_values("time")
        df.fillna(0, inplace=True)

        # Normaliser
        df_scaled = scaler.transform(df[features])
        last_60_days = df_scaled[-60:]

        if len(last_60_days) < 60:
            return {"prediction": "Pas assez de données pour prédire (besoin de 60 jours)"}

        last_60_days = np.array(last_60_days).reshape(1, 60, len(features))
        predicted_class = model.predict(last_60_days)
        predicted_label = np.argmax(predicted_class, axis=1)[0]

        classes = ['seche', 'moyenne', 'pluvieuse']
        return {"prediction": classes[predicted_label]}

    except Exception as e:
        return {"prediction": f"Erreur lors de la prédiction: {str(e)}"}
