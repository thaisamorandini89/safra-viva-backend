from . import db


class Responsavel(db.Model):
    __tablename__ = 'responsavel'
    id_responsavel = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cargo = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Responsavel {self.nome}>"
