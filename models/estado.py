from . import db
class Estado(db.Model):
    __tablename__ = 'estado'
    id_estado = db.Column(db.Integer, primary_key=True)
    uf_estado = db.Column(db.String(2), nullable=False)
    nome_estado = db.Column(db.String(100), nullable=False)