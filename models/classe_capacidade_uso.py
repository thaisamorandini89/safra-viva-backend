from . import db
class ClasseCapacidadeUso(db.Model):
    __tablename__ = 'classe_capacidade_uso'
    id_classe_capacidade_uso = db.Column(db.Integer, primary_key=True)
    sigla = db.Column(db.String(10), nullable=False, unique=True) # Ex: "I", "II", "VIII"
    descricao = db.Column(db.String(150), nullable=False)
    aptidao_principal = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<ClasseCapacidadeUso {self.sigla}>"