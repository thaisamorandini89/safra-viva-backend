from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Propriedade(db.Model):
    __tablename__ = 'propriedades'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    identificacao_legal = db.Column(db.String(100), unique=True, nullable=False)
    localizacao = db.Column(db.String(255), nullable=False)
    area = db.Column(db.Float, nullable=False)
    tipo_solo_id = db.Column(db.Integer, db.ForeignKey('tipos_solo.id'), nullable=False)
    classe_capacidade_uso_id = db.Column(db.Integer, db.ForeignKey('classes_capacidade_uso.id'), nullable=False)

    tipo_solo = db.relationship('TipoSolo', backref='propriedades')
    classe_capacidade_uso = db.relationship('ClasseCapacidadeUso', backref='propriedades')

    def __repr__(self):
        return f'<Propriedade {self.nome}>'