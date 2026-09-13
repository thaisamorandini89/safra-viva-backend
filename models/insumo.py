from . import db


class Insumo(db.Model):
    """
    Insumo = item de estoque vinculado a um Produto.
    Controla saldo, estoque mínimo e valor unitário.
    Os dados comerciais (nome, fabricante, marca, etc.) ficam no Produto.
    """
    __tablename__ = 'insumo'
    id_insumo = db.Column(db.Integer, primary_key=True)

    # Vinculação com o Produto
    id_produto = db.Column(
        db.Integer,
        db.ForeignKey('produto.id_produto'),
        nullable=False
    )

    # Controle de Estoque
    estoque_atual = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    estoque_minimo = db.Column(db.Numeric(14, 3), nullable=True, default=0)
    valor_unitario = db.Column(db.Numeric(14, 2), nullable=True, default=0)

    # Controle
    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Insumo id={self.id_insumo} produto={self.id_produto}>"
