import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping

# 1. Charger les données
df = pd.read_csv('precipitations_tunis.csv')  # Remplace par le nom de ton fichier
df['time'] = pd.to_datetime(df['time'])

# 2. Remplir les valeurs manquantes initiales
df.fillna(0, inplace=True)

# 3. Colonnes utilisées
features = ['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun']
df_features = df[features].copy()

# 4. Normalisation
scaler = StandardScaler()
df_scaled_values = scaler.fit_transform(df_features)
df_scaled = pd.DataFrame(df_scaled_values, columns=features)
df_scaled['time'] = df['time']

# 5. Ajout des infos temporelles
df_scaled['year'] = df['time'].dt.year
df_scaled['month'] = df['time'].dt.month
df_scaled['season'] = df_scaled['month'] % 12 // 3 + 1  # 1=winter, 2=spring...

# 6. Moyennes saisonnières
seasonal = df_scaled.groupby(['year', 'season'])[features].mean().reset_index()

# 7. Vérification et traitement des NaN
if seasonal.isnull().values.any():
    print("NaNs détectés dans les moyennes saisonnières. Suppression...")
    seasonal.dropna(inplace=True)  # Tu peux aussi utiliser un imputer si tu préfères

# 8. Clustering
X_cluster = seasonal[features]
kmeans = KMeans(n_clusters=3, random_state=0)
seasonal['label'] = kmeans.fit_predict(X_cluster)

# 9. Conversion des types pour merge
df_scaled['year'] = df_scaled['year'].astype(np.int64)
df_scaled['season'] = df_scaled['season'].astype(np.int64)
seasonal['year'] = seasonal['year'].astype(np.int64)
seasonal['season'] = seasonal['season'].astype(np.int64)

# 10. Fusion des labels avec les données journalières
df_labeled = df_scaled.merge(seasonal[['year', 'season', 'label']], on=['year', 'season'], how='left')

# 11. Création des séquences pour le LSTM
sequence_length = 60
X_seq, y_seq = [], []

data_array = df_labeled[features].values
labels_array = df_labeled['label'].values

for i in range(len(data_array) - sequence_length):
    X_seq.append(data_array[i:i+sequence_length])
    y_seq.append(labels_array[i + sequence_length])

X_seq = np.array(X_seq)
y_seq = np.array(y_seq)

# 12. Séparation train/test
X_train, X_test, y_train, y_test = train_test_split(X_seq, y_seq, test_size=0.2, random_state=42)

# 13. Modèle LSTM
model = Sequential([
    LSTM(64, input_shape=(sequence_length, len(features))),
    Dense(32, activation='relu'),
    Dense(3, activation='softmax')
])
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])


early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=32,
    validation_split=0.1,
    callbacks=[early_stop]
)

# 15. Évaluation
loss, acc = model.evaluate(X_test, y_test)
print(f"Accuracy: {acc:.2f}")



# 17. Prédiction pour la prochaine période
last_60_days = df_scaled[features].iloc[-60:].values
last_60_days = last_60_days.reshape((1, 60, len(features)))

predicted_class = model.predict(last_60_days)
predicted_label = np.argmax(predicted_class, axis=1)

# 18. Affichage du résultat
classes = ['seche', 'moyenne', 'pluvieuse']
print(f"La prochaine période est : {classes[predicted_label[0]]}")
# Dans ton code d’entraînement, ajoute après le fit :
model.save("season_lstm_model.h5")

# Et pour le scaler
import joblib
joblib.dump(scaler, "scaler.pkl")
