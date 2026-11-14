from . import db


class Maquina(db.Model):
    """
    Catalogo de Maquinas e Implementos.
    Ex.: Trator John Deere 6110J, Colheitadeira New Holland CR.
    """
    __tablename__ = 'maquina'

    id_maquina = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=True)
    observacoes = db.Column(db.String(500), nullable=True)
    status = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Maquina {self.nome}>"
