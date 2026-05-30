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

    result = train_prediction_model()

    return jsonify(result)


@prediction_bp.route(
    "/predict",
    methods=["POST"]
)
def predict():

    body = request.get_json()

    result = predict_price(body)

    return jsonify(result)