from . import db


class Fabricante(db.Model):
    __tablename__ = 'fabricante'
    id_fabricante = db.Column(db.Integer, primary_key=True)
    nome_fabricante = db.Column(db.String(150), nullable=False, unique=True)
    cnpj = db.Column(db.String(14), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.String(500), nullable=True)

    # Controle
    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Fabricante {self.nome_fabricante}>"
