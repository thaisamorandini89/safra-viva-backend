from . import db


class LoteInsumo(db.Model):
    """Lote de um insumo, com saldo próprio mantido pelas movimentações."""
    __tablename__ = 'lote_insumo'
    __table_args__ = (
        db.UniqueConstraint('id_insumo', 'numero_lote', name='lote_insumo_id_insumo_numero_lote_key'),
        db.CheckConstraint('quantidade >= 0', name='lote_insumo_quantidade_check'),
    )

    id_lote = db.Column(db.Integer, primary_key=True)
    id_insumo = db.Column(
        db.Integer,
        db.ForeignKey('insumo.id_insumo', name='lote_insumo_id_insumo_fkey'),
        nullable=False
    )
    numero_lote = db.Column(db.String(50), nullable=False)
    data_fabricacao = db.Column(db.Date, nullable=True)
    data_validade = db.Column(db.Date, nullable=True)
    quantidade = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<LoteInsumo {self.numero_lote} insumo={self.id_insumo} saldo={self.quantidade}>"
