from flask import Blueprint, g, jsonify, request

from services.auth_service import AuthService, serializar_usuario
from utils.auth import requer_auth

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    dados = request.get_json(silent=True) or {}
    usuario = AuthService.autenticar(dados.get('email'), dados.get('senha'))
    if usuario is None:
        return jsonify({"error": "E-mail ou senha inválidos."}), 401
    return jsonify({
        "token": AuthService.gerar_token(usuario),
        "usuario": serializar_usuario(usuario),
    }), 200


@auth_bp.route('/auth/me', methods=['GET'])
@requer_auth
def me():
    return jsonify(serializar_usuario(g.usuario)), 200
