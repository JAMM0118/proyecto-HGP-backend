from werkzeug.security import check_password_hash, generate_password_hash
from .model import create_user, find_user_by_email, find_user_by_id, update_user_last_login, add_token_to_blacklist
from .validators import validate_email_format, validate_password_strength, validate_user_role
from .jwt_utils import generate_token

def register_user(data):
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    name = (data.get("name") or "").strip()
    role = (data.get("role") or "").strip().lower()

    if not email or not password or not name or not role:
        return {"error": "Email, contraseña, nombre y tipo de usuario son requeridos"}, 400

    is_valid_email, email_error = validate_email_format(email)
    if not is_valid_email:
        return {"error": f"Email inválido: {email_error}"}, 400

    is_valid_password, password_error = validate_password_strength(password)
    if not is_valid_password:
        return {"error": password_error}, 400

    is_valid_role, role_error = validate_user_role(role)
    if not is_valid_role:
        return {"error": role_error}, 400

    if find_user_by_email(email):
        return {"error": "El usuario ya existe"}, 409

    if len(name) < 2:
        return {"error": "El nombre debe tener al menos 2 caracteres"}, 400

    hashed_password = generate_password_hash(password)
    user = {
        "email": email,
        "password": hashed_password,
        "name": name,
        "role": role,
    }

    user_id = create_user(user)

    return {
        "message": "Usuario registrado correctamente",
        "user": {
            "id": str(user_id),
            "email": email,
            "name": name,
            "role": role
        }
    }, 201


def authenticate_user(data):
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return {"error": "Email y contraseña son requeridos"}, 400

    user = find_user_by_email(email)
    if not user or not check_password_hash(user.get("password", ""), password):
        return {"error": "Credenciales inválidas"}, 401

    if not user.get("is_active", True):
        return {"error": "Usuario desactivado"}, 403

    update_user_last_login(user["_id"])

    token = generate_token(user["_id"], user.get("email"))

    user_data = {
        "id": str(user["_id"]),
        "email": user.get("email"),
        "name": user.get("name"),
        "role": user.get("role", "invitado"),
    }

    return {
        "message": "Inicio de sesión exitoso",
        "user": user_data,
        "token": token
    }, 200


def logout_user(token):
    """Add token to blacklist"""
    try:
        add_token_to_blacklist(token)
        return {"message": "Sesión cerrada exitosamente"}, 200
    except Exception as e:
        return {"error": "Error al cerrar sesión"}, 500
