from . import db

STATUS_ATIVIDADE = ("Planejada", "Em Andamento", "Concluída")


class AtividadeAgricola(db.Model):
    """
    Operacao agricola executada em um talhao (o que o formulario de
    'Cadastro de Atividade' registra).
    """
    __tablename__ = 'atividade_agricola'

    id_atividade_agricola = db.Column(db.Integer, primary_key=True)

    id_categoria_atividade = db.Column(
        db.Integer,
        db.ForeignKey('categoria_atividade.id_categoria_atividade'),
        nullable=False
    )
    id_tipo_atividade = db.Column(
        db.Integer,
        db.ForeignKey('tipo_atividade.id_atividade'),
        nullable=False
    )
    id_talhao = db.Column(
        db.Integer,
        db.ForeignKey('talhao.id_talhao'),
        nullable=False
    )
    id_propriedade = db.Column(
        db.Integer,
        db.ForeignKey('propriedade.id_propriedade'),
        nullable=True
    )
    id_empresa = db.Column(db.Integer, nullable=True)
    safra = db.Column(db.String(20), nullable=True)
    id_funcionario = db.Column(
        db.String(36),
        db.ForeignKey('funcionario.id_funcionario'),
        nullable=True
    )

    status = db.Column(
        db.Enum(*STATUS_ATIVIDADE, name='status_atividade'),
        nullable=False,
        default='Planejada'
    )

    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=True)
    custo_operacao = db.Column(db.Numeric(14, 2), nullable=True)
    observacoes = db.Column(db.String(1000), nullable=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    categoria = db.relationship('CategoriaAtividade', lazy='joined')
    tipo = db.relationship('TipoAtividade', lazy='joined')
    talhao = db.relationship('Talhao', lazy='joined')
    propriedade = db.relationship('Propriedade', lazy='joined')
    funcionario = db.relationship('Funcionario', lazy='joined')
    insumos = db.relationship(
        'AtividadeInsumo',
        backref='atividade',
        cascade='all, delete-orphan',
        lazy='selectin',
        # sem isto, o item atualizado pela baixa de estoque muda de posição na lista
        order_by='AtividadeInsumo.id'
    )
    maquinas = db.relationship(
        'AtividadeMaquina',
        backref='atividade',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    def __repr__(self):
        return f"<AtividadeAgricola id={self.id_atividade_agricola} status={self.status}>"
