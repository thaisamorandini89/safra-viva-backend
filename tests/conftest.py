import pytest

from app import create_app
from models import db as _db


@pytest.fixture()
def app():
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
        'JWT_SECRET': 'segredo-de-teste-com-32-caracteres-ou-mais',
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
