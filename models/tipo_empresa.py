from . import db
class TipoEmpresa(db.Model):
    __tablename__ = 'tipo_empresa'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)