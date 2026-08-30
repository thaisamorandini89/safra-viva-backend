from sqlalchemy import Column, Integer, String
from models import db

class TipoEmpresa(db.Model):
    __tablename__ = 'tipo_empresa'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)

    def __repr__(self):
        return f'<TipoEmpresa {self.nome}>'