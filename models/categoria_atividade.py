from . import db


class CategoriaAtividade(db.Model):
    """
    Categoria de atividade agricola (catalogo).
    Ex.: Preparo de Solo, Plantio, Tratos Culturais, Irrigacao, Colheita.
    """
    __tablename__ = 'categoria_atividade'

    id_categoria_atividade = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False, unique=True)
    status = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<CategoriaAtividade {self.nome}>"
