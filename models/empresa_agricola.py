from . import db
class EmpresaAgricola(db.Model):
    __tablename__ = 'empresa_agricola'
    id_empresa = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(200), nullable=False)
    nome_fantasia = db.Column(db.String(200))
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    inscricao_estadual = db.Column(db.String(20))
    inscricao_municipal = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    website = db.Column(db.String(100))
    data_fundacao = db.Column(db.Date)
    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())
    
    id_tipo_empresa = db.Column(db.Integer, db.ForeignKey('tipo_empresa.id'))
    id_regime_tributario = db.Column(db.Integer, db.ForeignKey('regime_tributario.id'))
    id_logradouro = db.Column(db.Integer, db.ForeignKey('logradouro.id_logradouro'))