from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EmpresaAgricola(db.Model):
    __tablename__ = 'empresa_agricola'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(15), nullable=True)
    
    def __repr__(self):
        return f'<EmpresaAgricola {self.nome}>'