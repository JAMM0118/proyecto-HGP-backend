from flask import Blueprint, jsonify, request
from .service import authenticate_user, register_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True, silent=True) or {}
    result, status = register_user(data)
    return jsonify(result), status


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    result, status = authenticate_user(data)
    return jsonify(result), status
