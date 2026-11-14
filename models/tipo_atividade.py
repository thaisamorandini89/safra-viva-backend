from . import db


class TipoAtividade(db.Model):
    """
    Tipo de atividade agricola (catalogo).
    Ex.: Aracao, Gradagem, Adubacao, Pulverizacao, Calagem.
    Mantem a PK 'id_atividade' para preservar a FK de movimentacao_estoque.
    """
    __tablename__ = 'tipo_atividade'

    id_atividade = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    id_categoria_atividade = db.Column(
        db.Integer,
        db.ForeignKey('categoria_atividade.id_categoria_atividade'),
        nullable=False
    )
    status = db.Column(db.Boolean, default=True)

    categoria = db.relationship('CategoriaAtividade', lazy='joined')

    def __repr__(self):
        return f"<TipoAtividade {self.descricao}>"
