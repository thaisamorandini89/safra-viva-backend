from . import db


class Safra(db.Model):
    """Safra agrícola — período, cultura e área vinculados a uma propriedade."""
    __tablename__ = 'safra'

    id_safra = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(200), nullable=False)
    cultura = db.Column(db.String(100), nullable=False)

    id_propriedade = db.Column(
        db.Integer,
        db.ForeignKey('propriedade.id_propriedade'),
        nullable=False
    )

    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=True)
    area_plantada = db.Column(db.Numeric(12, 2), nullable=True)

    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Safra {self.nome} ({self.cultura})>"
