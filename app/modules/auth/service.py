from werkzeug.security import check_password_hash, generate_password_hash
from .model import create_user, find_user_by_email


def register_user(data):
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    name = (data.get("name") or "").strip()

    if not email or not password:
        return {"error": "Email y contraseña son requeridos"}, 400

    if find_user_by_email(email):
        return {"error": "El usuario ya existe"}, 400

    hashed_password = generate_password_hash(password)
    user = {
        "email": email,
        "password": hashed_password,
        "name": name,
    }

    create_user(user)

    return {"message": "Usuario registrado correctamente"}, 201


def authenticate_user(data):
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return {"error": "Email y contraseña son requeridos"}, 400

    user = find_user_by_email(email)
    if not user or not check_password_hash(user.get("password", ""), password):
        return {"error": "Credenciales inválidas"}, 401

    user_data = {
        "email": user.get("email"),
        "name": user.get("name"),
    }

    return {"message": "Inicio de sesión exitoso", "user": user_data}, 200
