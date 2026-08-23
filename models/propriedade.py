from . import db
class Propriedade(db.Model):
    __tablename__ = 'propriedade'
    id_propriedade = db.Column(db.Integer, primary_key=True)

    # Vinculação
    nome_propriedade = db.Column(db.String(200), nullable=False)
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa_agricola.id_empresa'), nullable=False)

    # Identificação Legal
    car = db.Column(db.String(60), nullable=False)   # Cadastro Ambiental Rural
    ccir = db.Column(db.String(30), nullable=True)   # Certificado de Cadastro de Imóvel Rural
    nirf = db.Column(db.String(30), nullable=True)   # Número do Imóvel na Receita Federal

    # Localização
    id_logradouro = db.Column(db.Integer, db.ForeignKey('logradouro.id_logradouro'), nullable=True)
    ponto_referencia = db.Column(db.String(200), nullable=True)

    # Coordenadas Geográficas
    latitude = db.Column(db.Numeric(11, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)

    # Dados Físicos (em hectares, exceto altitude em metros)
    area_total = db.Column(db.Numeric(12, 2), nullable=False)
    area_agricultavel = db.Column(db.Numeric(12, 2), nullable=False)
    area_preservacao = db.Column(db.Numeric(12, 2), nullable=False)
    area_pastagem = db.Column(db.Numeric(12, 2), nullable=True)
    area_vegetacao_nativa = db.Column(db.Numeric(12, 2), nullable=True)
    altitude_media = db.Column(db.Integer, nullable=True)

    # Outras Informações
    id_tipo_solo = db.Column(db.Integer, db.ForeignKey('tipo_solo.id'), nullable=True)
    id_classe_capacidade_uso = db.Column(
        db.Integer,
        db.ForeignKey('classe_capacidade_uso.id_classe_capacidade_uso'),
        nullable=True
    )
    observacoes = db.Column(db.String(500), nullable=True)

    # Controle
    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Propriedade {self.nome_propriedade}>"
