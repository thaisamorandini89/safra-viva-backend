import uuid

from . import db


class FuncionarioPropriedade(db.Model):
    """Vínculo entre um funcionário e uma propriedade."""
    __tablename__ = 'funcionario_propriedade'

    id_funcionario_propriedade = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    id_funcionario = db.Column(
        db.String(36),
        db.ForeignKey('funcionario.id_funcionario'),
        nullable=False
    )
    id_propriedade = db.Column(
        db.Integer,
        db.ForeignKey('propriedade.id_propriedade'),
        nullable=False
    )
    data_vinculacao = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<FuncionarioPropriedade func={self.id_funcionario} prop={self.id_propriedade}>"
