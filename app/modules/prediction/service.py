import os
import joblib
import pandas as pd

from datetime import datetime

from .model import save_prediction
from .trainer import train_model

MODEL_PATH = "app/models/property_price_model.pkl"


def train_prediction_model():
    return train_model()


def predict_price(data):

    if not os.path.exists(MODEL_PATH):
        raise Exception(
            "Modelo no entrenado"
        )

    model = joblib.load(MODEL_PATH)

    features = pd.DataFrame([
        {
            "area_construida": float(data["area_construida"]),
            "habitaciones": int(data["habitaciones"]),
            "banos": int(data["banos"]),
            "tipo_propiedad": str(data["tipo_propiedad"]).lower().strip(),
            "ciudad": str(data["ciudad"]).lower().strip()
        }
    ])

    prediction = model.predict(features)[0]

    result = {
        "fecha": datetime.utcnow().isoformat(),
        "area_construida": float(data["area_construida"]),
        "habitaciones": int(data["habitaciones"]),
        "banos": int(data["banos"]),
        "tipo_propiedad": str(data["tipo_propiedad"]).lower().strip(),
        "ciudad": str(data["ciudad"]).lower().strip(),
        "precio_estimado": round(float(prediction), 0)
    }

    save_prediction(result)
    result.pop("_id", None)

    return result