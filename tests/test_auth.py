import datetime

import jwt
import pytest

from models import db
from models.usuario import Usuario
from services.auth_service import AuthService, SENHA_DEMO


@pytest.fixture()
def usuarios(app):
    AuthService.garantir_usuarios_demo()
    return {u.perfil: u for u in Usuario.query.all()}


def _login(client, email, senha):
    return client.post('/api/auth/login', json={'email': email, 'senha': senha})


def test_login_valido_devolve_token_sem_senha(client, usuarios):
    resp = _login(client, 'karla@safraviva.com.br', SENHA_DEMO)
    assert resp.status_code == 200
    corpo = resp.get_json()
    assert corpo['token']
    assert corpo['usuario']['perfil'] == 'administrador'
    assert 'senha_hash' not in corpo['usuario']
    assert 'senha_hash' not in str(corpo)


def test_login_senha_errada(client, usuarios):
    resp = _login(client, 'karla@safraviva.com.br', 'errada')
    assert resp.status_code == 401


def test_login_usuario_inativo(client, usuarios):
    usuarios['administrador'].ativo = False
    db.session.commit()
    resp = _login(client, 'karla@safraviva.com.br', SENHA_DEMO)
    assert resp.status_code == 401


def test_me_sem_token(client, usuarios):
    assert client.get('/api/auth/me').status_code == 401


def test_me_com_token(client, usuarios):
    token = _login(client, 'joao.silva@safraviva.com.br', SENHA_DEMO).get_json()['token']
    resp = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    corpo = resp.get_json()
    assert corpo['perfil'] == 'agronomo'
    assert 'senha_hash' not in corpo


def test_token_expirado(app, client, usuarios):
    agora = datetime.datetime.now(datetime.timezone.utc)
    token = jwt.encode(
        {'sub': str(usuarios['agronomo'].id_usuario), 'exp': agora - datetime.timedelta(minutes=1)},
        app.config['JWT_SECRET'],
        algorithm='HS256',
    )
    resp = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 401


def test_token_assinatura_invalida(client, usuarios):
    token = jwt.encode({'sub': '1'}, 'outro-segredo-com-32-caracteres-ou-mais', algorithm='HS256')
    resp = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 401
