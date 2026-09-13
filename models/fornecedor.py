from . import db


class Fornecedor(db.Model):
    __tablename__ = 'fornecedor'
    id_fornecedor = db.Column(db.Integer, primary_key=True)
    nome_fornecedor = db.Column(db.String(200), nullable=False)
    nome_fantasia = db.Column(db.String(200), nullable=True)
    cnpj = db.Column(db.String(14), nullable=True, unique=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    id_logradouro = db.Column(db.Integer, db.ForeignKey('logradouro.id_logradouro'), nullable=True)
    observacoes = db.Column(db.String(500), nullable=True)

    # Controle
    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Fornecedor {self.nome_fornecedor}>"
