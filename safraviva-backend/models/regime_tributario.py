from sqlalchemy import Column, Integer, String
from models import db

class RegimeTributario(db.Model):
    __tablename__ = 'regime_tributario'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)

    def __repr__(self):
        return f'<RegimeTributario {self.nome}>'