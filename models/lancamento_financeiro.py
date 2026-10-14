import uuid

from . import db


class LancamentoFinanceiro(db.Model):
    """
    Lançamento financeiro (receita ou despesa) da operação agrícola.
    Pode ser vinculado a empresa, propriedade, talhão, safra e centro de custo,
    e distribuído entre talhões via RateioLancamento.
    """
    __tablename__ = 'lancamento_financeiro'

    id_lancamento = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    tipo = db.Column(db.String(10), nullable=False)  # RECEITA | DESPESA
    categoria = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500), nullable=True)
    valor = db.Column(db.Numeric(14, 2), nullable=False)
    data_lancamento = db.Column(db.Date, nullable=False)

    forma_pagamento = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(10), nullable=False, default='PENDENTE')
    conciliado = db.Column(db.Boolean, nullable=False, default=False)
    observacao = db.Column(db.String(500), nullable=True)

    # Vínculos (opcionais)
    id_empresa = db.Column(
        db.Integer, db.ForeignKey('empresa_agricola.id_empresa'), nullable=True
    )
    id_propriedade = db.Column(
        db.Integer, db.ForeignKey('propriedade.id_propriedade'), nullable=True
    )
    id_talhao = db.Column(
        db.Integer, db.ForeignKey('talhao.id_talhao'), nullable=True
    )
    id_safra = db.Column(
        db.Integer, db.ForeignKey('safra.id_safra'), nullable=True
    )
    id_centro_custo = db.Column(
        db.Integer, db.ForeignKey('centro_custo.id_centro_custo'), nullable=True
    )

    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    rateios = db.relationship(
        'RateioLancamento',
        backref='lancamento',
        cascade='all, delete-orphan',
        lazy='select'
    )

    def __repr__(self):
        return f"<LancamentoFinanceiro {self.tipo} {self.categoria} {self.valor}>"
