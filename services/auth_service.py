import datetime

import jwt
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from models import db
from models.usuario import Usuario

SENHA_DEMO = 'Safra@2025'
EXPIRACAO_HORAS = 8

USUARIOS_DEMO = [
    ('Karla Klemke', 'karla@safraviva.com.br', 'administrador'),
    ('João Silva', 'joao.silva@safraviva.com.br', 'agronomo'),
    ('Maria Souza', 'maria.souza@safraviva.com.br', 'financeiro'),
    ('Carlos Lima', 'carlos.lima@safraviva.com.br', 'supervisor-campo'),
    ('Ana Pereira', 'ana.pereira@safraviva.com.br', 'estoquista'),
]


def serializar_usuario(usuario):
    return {
        'id': usuario.id_usuario,
        'nome': usuario.nome,
        'email': usuario.email,
        'perfil': usuario.perfil,
        'id_empresa': usuario.id_empresa,
    }


class AuthService:
    @staticmethod
    def hash_senha(senha):
        return generate_password_hash(senha)

    @staticmethod
    def autenticar(email, senha):
        """Devolve o usuário se as credenciais forem válidas e ele estiver ativo."""
        usuario = Usuario.query.filter(
            db.func.lower(Usuario.email) == (email or '').strip().lower()
        ).first()
        if usuario is None or not usuario.ativo:
            return None
        if not check_password_hash(usuario.senha_hash, senha or ''):
            return None
        return usuario

    @staticmethod
    def gerar_token(usuario):
        agora = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            'sub': str(usuario.id_usuario),
            'perfil': usuario.perfil,
            'id_empresa': usuario.id_empresa,
            'iat': agora,
            'exp': agora + datetime.timedelta(hours=EXPIRACAO_HORAS),
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')

    @staticmethod
    def validar_token(token):
        """Devolve o usuário ativo do token ou None se inválido/expirado."""
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
        except jwt.PyJWTError:
            return None
        usuario = db.session.get(Usuario, int(payload['sub']))
        if usuario is None or not usuario.ativo:
            return None
        return usuario

    @staticmethod
    def garantir_usuarios_demo(id_empresa=None):
        """Cria os usuários de demonstração que ainda não existem."""
        criados = 0
        for nome, email, perfil in USUARIOS_DEMO:
            if Usuario.query.filter_by(email=email).first():
                continue
            db.session.add(Usuario(
                nome=nome,
                email=email,
                perfil=perfil,
                id_empresa=id_empresa,
                senha_hash=AuthService.hash_senha(SENHA_DEMO),
            ))
            criados += 1
        db.session.commit()
        return criados
