import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
from .model import is_token_blacklisted

def generate_token(user_id, email):
    """Generate JWT token for user"""
    payload = {
        'user_id': str(user_id),
        'email': email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=current_app.config.get("JWT_EXPIRATION_HOURS", 24))
    }
    token = jwt.encode(
        payload,
        current_app.config.get("JWT_SECRET_KEY"),
        algorithm=current_app.config.get("JWT_ALGORITHM", "HS256")
    )
    return token

def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        # Check if token is blacklisted (logged out)
        if is_token_blacklisted(token):
            return None
        
        payload = jwt.decode(
            token,
            current_app.config.get("JWT_SECRET_KEY"),
            algorithms=[current_app.config.get("JWT_ALGORITHM", "HS256")]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to protect routes requiring authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        return f(payload, *args, **kwargs)
    
    return decorated
