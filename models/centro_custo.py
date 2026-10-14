from . import db


class CentroCusto(db.Model):
    """Centro de custo operacional ou administrativo para classificar despesas."""
    __tablename__ = 'centro_custo'

    id_centro_custo = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # OPERACIONAL | ADMINISTRATIVO
    descricao = db.Column(db.String(500), nullable=True)

    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<CentroCusto {self.nome} ({self.tipo})>"
