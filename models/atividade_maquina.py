from . import db


class AtividadeMaquina(db.Model):
    """Maquina/implemento usado em uma atividade agricola (FK para Maquina + snapshot)."""
    __tablename__ = 'atividade_maquina'

    id = db.Column(db.Integer, primary_key=True)
    id_atividade_agricola = db.Column(
        db.Integer,
        db.ForeignKey('atividade_agricola.id_atividade_agricola', ondelete='CASCADE'),
        nullable=False
    )
    id_maquina = db.Column(
        db.Integer,
        db.ForeignKey('maquina.id_maquina'),
        nullable=False
    )
    nome = db.Column(db.String(200), nullable=True)      # snapshot
    horas = db.Column(db.Numeric(10, 2), nullable=True)
    custo = db.Column(db.Numeric(14, 2), nullable=True)

    def __repr__(self):
        return f"<AtividadeMaquina maquina={self.id_maquina} horas={self.horas}>"
