from . import db


class Atividade(db.Model):
    """
    Atividade agrícola (pulverização, adubação, calagem, etc.).
    Usada para rastrear a finalidade das saídas de estoque.
    """
    __tablename__ = 'atividade'

    id_atividade = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    data_atividade = db.Column(db.Date, nullable=True)
    status = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Atividade {self.descricao}>"
