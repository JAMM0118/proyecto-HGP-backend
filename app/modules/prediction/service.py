import os
import joblib

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

    features = [[
        data["area_construida"],
        data["habitaciones"],
        data["banos"],
        data["tipo_propiedad"],
        data["ciudad"]
    ]]

    prediction = model.predict(features)[0]

    result = {
        "fecha": datetime.utcnow().isoformat(),
        "area_construida": data["area_construida"],
        "habitaciones": data["habitaciones"],
        "banos": data["banos"],
        "tipo_propiedad": data["tipo_propiedad"],
        "ciudad": data["ciudad"],
        "precio_estimado": round(float(prediction), 0)
    }

    save_prediction(result)

    result.pop("_id", None)

    return result