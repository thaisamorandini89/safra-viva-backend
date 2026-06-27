from . import db
class Logradouro(db.Model):
    __tablename__ = 'logradouro'
    id_logradouro = db.Column(db.Integer, primary_key=True)
    cep = db.Column(db.String(8), nullable=False)
    logradouro = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(100))
    id_bairro = db.Column(db.Integer, db.ForeignKey('bairro.id_bairro'), nullable=False)