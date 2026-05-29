from flask import Blueprint, jsonify, request
from .service import authenticate_user, register_user, logout_user
from .jwt_utils import token_required, verify_token
from .model import find_user_by_id
from app.extensions.limiter import limiter

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per hour")
def register():
    """
    Endpoint para registrar un nuevo usuario
    ---

    tags:
        - Autenticación

    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              email:
                type: string
                example: user@example.com
              password:
                type: string
                example: strongpassword123
              role:
                type: string
                example: usuario
    responses:
      200:
        description: Usuario registrado correctamente
    """
    data = request.get_json(force=True, silent=True) or {}
    result, status = register_user(data)
    return jsonify(result), status


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per hour")
def login():
    """
    Endpoint para autenticar un usuario
    ---
    tags:
      - Autenticación
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              email:
                type: string
                example: user@example.com
              password:
                type: string
                example: strongpassword123
    responses:
      200:
        description: Usuario autenticado correctamente
    """
    data = request.get_json(force=True, silent=True) or {}
    result, status = authenticate_user(data)
    return jsonify(result), status


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(token_payload):
    """Logout endpoint - requires valid token
    ---

    tags:
      - Autenticación

    parameters:
        - name: Authorization
          in: header
          required: true
          type: string
          description: Token de autenticación (Bearer <token>)
    responses:
      200:
        description: Usuario deslogueado correctamente
    """
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(" ")[1] if " " in auth_header else None
        
        if not token:
            return jsonify({"error": "Token no encontrado"}), 400
        
        result, status = logout_user(token)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": "Error al cerrar sesión"}), 500


@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile(token_payload):
    """
    Endpoint para obtener el perfil de un usuario
    ---
    tags:
      - Autenticación
    parameters:
        - name: Authorization
          in: header
          required: true
          type: string
          description: Token de autenticación (Bearer <token>)
    responses:
      200:
        description: Perfil del usuario obtenido correctamente
    """
    try:
        user = find_user_by_id(token_payload["user_id"])
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify({
            "user": {
                "id": str(user["_id"]),
                "email": user.get("email"),
                "name": user.get("name"),
                "role": user.get("role", "invitado"),
                "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
                "last_login": user.get("last_login").isoformat() if user.get("last_login") else None,
            }
        }), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener perfil"}), 500
