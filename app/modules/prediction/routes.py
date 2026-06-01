from flask import Blueprint
from flask import request
from flask import jsonify

from .service import (
    predict_price,
    train_prediction_model
)

prediction_bp = Blueprint(
    "prediction",
    __name__
)


@prediction_bp.route(
    "/train",
    methods=["POST"]
)
def train():
    """
    Entrenar el modelo de predicción
    ---
    tags:
      - Prediction
    responses:
      200:
        description: Modelo entrenado correctamente

    """
    result = train_prediction_model()

    return jsonify(result)


@prediction_bp.route(
    "/predict",
    methods=["POST"]
)
def predict():
    """
    Predecir el precio de una propiedad
    ---
    tags:
      - Prediction
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            ciudad:
              type: string
              example: Bogotá
            area_construida:
              type: number
              example: 120.5
            habitaciones:
              type: integer
              example: 3
            tipo_propiedad:
              type: string
              example: apartamento
            banos:
              type: integer
              example: 2
    """
    body = request.get_json()
    result = predict_price(body)

    return jsonify(result)