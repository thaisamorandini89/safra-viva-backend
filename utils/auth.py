from functools import wraps

from flask import g, jsonify, request

from services.auth_service import AuthService


def requer_auth(func):
    """Exige token Bearer válido e expõe o usuário autenticado em g.usuario."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cabecalho = request.headers.get('Authorization', '')
        partes = cabecalho.split(' ', 1)
        if len(partes) != 2 or partes[0].lower() != 'bearer' or not partes[1].strip():
            return jsonify({"error": "Autenticação necessária."}), 401
        usuario = AuthService.validar_token(partes[1].strip())
        if usuario is None:
            return jsonify({"error": "Token inválido ou expirado."}), 401
        g.usuario = usuario
        return func(*args, **kwargs)
    return wrapper
