from flask import Blueprint, jsonify, request
from .service import authenticate_user, register_user
from .jwt_utils import token_required, verify_token
from .model import find_user_by_id
from app.extensions.limiter import limiter

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per hour")
def register():
    data = request.get_json(force=True, silent=True) or {}
    result, status = register_user(data)
    return jsonify(result), status


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per hour")
def login():
    data = request.get_json(force=True, silent=True) or {}
    result, status = authenticate_user(data)
    return jsonify(result), status


@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile(token_payload):
    try:
        user = find_user_by_id(token_payload["user_id"])
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify({
            "user": {
                "id": str(user["_id"]),
                "email": user.get("email"),
                "name": user.get("name"),
                "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
                "last_login": user.get("last_login").isoformat() if user.get("last_login") else None,
            }
        }), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener perfil"}), 500
