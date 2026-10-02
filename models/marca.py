from . import db


class Marca(db.Model):
    __tablename__ = 'marca'
    id_marca = db.Column(db.Integer, primary_key=True)
    descricao_marca = db.Column(db.String(500), nullable=False, unique=True)

    def __repr__(self):
        return f"<Marca {self.descricao_marca}>"
