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
    valor_unitario = db.Column(db.Numeric(14, 2), nullable=True)
    data_movimentacao = db.Column(db.DateTime, server_default=db.func.now())
    id_funcionario = db.Column(
        db.String(36),
        db.ForeignKey('funcionario.id_funcionario'),
        nullable=True
    )
    observacao = db.Column(db.String(500), nullable=True)

    # --- Dados da Entrada (preenchidos apenas quando tipo = ENTRADA) ---
    id_fornecedor = db.Column(
        db.Integer,
        db.ForeignKey('fornecedor.id_fornecedor'),
        nullable=True
    )
    numero_nota_fiscal = db.Column(db.String(50), nullable=True)
    numero_lote = db.Column(db.String(50), nullable=True)
    data_fabricacao = db.Column(db.Date, nullable=True)
    data_validade = db.Column(db.Date, nullable=True)

    # --- Destino e Rastreabilidade (preenchidos apenas quando tipo = SAIDA) ---
    id_talhao = db.Column(
        db.Integer,
        db.ForeignKey('talhao.id_talhao'),
        nullable=True
    )
    safra = db.Column(db.String(20), nullable=True)
    id_atividade = db.Column(
        db.Integer,
        db.ForeignKey('atividade.id_atividade'),
        nullable=True
    )
    destino_finalidade = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<MovimentacaoEstoque {self.tipo_movimentacao} insumo={self.id_insumo} qtd={self.quantidade}>"
