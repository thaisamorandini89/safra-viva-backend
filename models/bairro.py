from . import db
class Bairro(db.Model):
    __tablename__ = 'bairro'
    id_bairro = db.Column(db.Integer, primary_key=True)
    nome_bairro = db.Column(db.String(100), nullable=False)
    id_cidade = db.Column(db.Integer, db.ForeignKey('cidade.id_cidade'), nullable=False)