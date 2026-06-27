from . import db
class RegimeTributario(db.Model):
    __tablename__ = 'regime_tributario'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
