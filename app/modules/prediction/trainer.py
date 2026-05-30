import os
import joblib
import pandas as pd

from catboost import CatBoostRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import train_test_split

from .model import get_training_data

MODEL_PATH = "app/models/property_price_model.pkl"


def train_model():

    data = get_training_data()

    if not data:
        raise Exception("No hay datos para entrenar")

    rows = []

    for doc in data:

        rows.append({
            "area_construida": doc.get("area_construida"),
            "habitaciones": doc.get("habitaciones"),
            "banos": doc.get("banos"),
            "tipo_propiedad": doc.get("propiedad", {}).get("tipo_propiedad"),
            "ciudad": doc.get("ubicacion", {}).get("ciudad"),
            "precio": doc.get("precio")
        })

    df = pd.DataFrame(rows)

    df = df.dropna()

    X = df[
        [
            "area_construida",
            "habitaciones",
            "banos",
            "tipo_propiedad",
            "ciudad"
        ]
    ]

    y = df["precio"]

    categorical_features = [
        "tipo_propiedad",
        "ciudad"
    ]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = CatBoostRegressor(
        iterations=500,
        depth=8,
        learning_rate=0.1,
        loss_function="RMSE",
        verbose=False
    )

    model.fit(
        X_train,
        y_train,
        cat_features=categorical_features
    )

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    os.makedirs("app/models", exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    return {
        "records": len(df),
        "mae": round(float(mae), 2),
        "mse": round(float(mse), 2),
        "r2": round(float(r2), 4)
    }