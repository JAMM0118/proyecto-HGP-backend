from werkzeug.security import check_password_hash, generate_password_hash
from .model import create_user, find_user_by_email, find_user_by_id, update_user_last_login
from .validators import validate_email_format, validate_password_strength
from .jwt_utils import generate_token

def register_user(data):
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    name = (data.get("name") or "").strip()

    if not email or not password or not name:
        return {"error": "Email, contraseña y nombre son requeridos"}, 400

    is_valid_email, email_error = validate_email_format(email)
    if not is_valid_email:
        return {"error": f"Email inválido: {email_error}"}, 400

    is_valid_password, password_error = validate_password_strength(password)
    if not is_valid_password:
        return {"error": password_error}, 400

    if find_user_by_email(email):
        return {"error": "El usuario ya existe"}, 409

    if len(name) < 2:
        return {"error": "El nombre debe tener al menos 2 caracteres"}, 400

    hashed_password = generate_password_hash(password)
    user = {
        "email": email,
        "password": hashed_password,
        "name": name,
    }

    user_id = create_user(user)

    return {
        "message": "Usuario registrado correctamente",
        "user": {
            "id": str(user_id),
            "email": email,
            "name": name
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
    }

    return {
        "message": "Inicio de sesión exitoso",
        "user": user_data,
        "token": token
    }, 200
