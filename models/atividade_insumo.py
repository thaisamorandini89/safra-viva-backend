from . import db


class AtividadeInsumo(db.Model):
    """Insumo utilizado em uma atividade agricola (FK para Insumo + snapshot)."""
    __tablename__ = 'atividade_insumo'

    id = db.Column(db.Integer, primary_key=True)
    id_atividade_agricola = db.Column(
        db.Integer,
        db.ForeignKey('atividade_agricola.id_atividade_agricola', ondelete='CASCADE'),
        nullable=False
    )
    id_insumo = db.Column(
        db.Integer,
        db.ForeignKey('insumo.id_insumo'),
        nullable=False
    )
    nome = db.Column(db.String(200), nullable=True)      # snapshot
    unidade = db.Column(db.String(20), nullable=True)    # snapshot
    quantidade = db.Column(db.Numeric(14, 3), nullable=True)
    custo = db.Column(db.Numeric(14, 2), nullable=True)

    def __repr__(self):
        return f"<AtividadeInsumo insumo={self.id_insumo} qtd={self.quantidade}>"
