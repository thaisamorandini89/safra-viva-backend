import uuid

from . import db


class MovimentacaoEstoque(db.Model):
    """
    Registro de entrada/saída de estoque de um Insumo.
    O saldo (estoque_atual) do insumo é atualizado na mesma transação.
    """
    __tablename__ = 'movimentacao_estoque'

    id_movimentacao = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    id_insumo = db.Column(
        db.Integer,
        db.ForeignKey('insumo.id_insumo'),
        nullable=False
    )
    tipo_movimentacao = db.Column(db.String(10), nullable=False)  # ENTRADA | SAIDA
    quantidade = db.Column(db.Numeric(10, 2), nullable=False)
    data_movimentacao = db.Column(db.DateTime, server_default=db.func.now())
    id_responsavel = db.Column(
        db.Integer,
        db.ForeignKey('responsavel.id_responsavel'),
        nullable=True
    )
    observacao = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<MovimentacaoEstoque {self.tipo_movimentacao} insumo={self.id_insumo} qtd={self.quantidade}>"
