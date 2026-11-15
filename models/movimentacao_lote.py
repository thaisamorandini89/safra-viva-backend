from . import db


class MovimentacaoLote(db.Model):
    """Quantidade que uma movimentação de estoque colocou em um lote ou tirou dele."""
    __tablename__ = 'movimentacao_lote'

    id = db.Column(db.Integer, primary_key=True)
    id_movimentacao = db.Column(
        db.String(36),
        db.ForeignKey(
            'movimentacao_estoque.id_movimentacao',
            name='movimentacao_lote_id_movimentacao_fkey',
            ondelete='CASCADE'
        ),
        nullable=False
    )
    id_lote = db.Column(
        db.Integer,
        db.ForeignKey('lote_insumo.id_lote', name='movimentacao_lote_id_lote_fkey'),
        nullable=False
    )
    quantidade = db.Column(db.Numeric(14, 3), nullable=False)

    def __repr__(self):
        return f"<MovimentacaoLote mov={self.id_movimentacao} lote={self.id_lote} qtd={self.quantidade}>"
