from flask import Blueprint, jsonify
from .service import get_message

test_bp = Blueprint("test", __name__)

@test_bp.route("/")
def home():
    """
    Endpoint de prueba
    ---
    responses:
      200:
        description: Mensaje de prueba
    """
    return jsonify(get_message())