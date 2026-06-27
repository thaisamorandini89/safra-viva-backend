from . import db
class TipoSolo(db.Model):
    __tablename__ = 'tipo_solo'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False, unique=True)
    sigla = db.Column(db.String(10), nullable=True)
    classe_textural = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<TipoSolo {self.descricao}>"