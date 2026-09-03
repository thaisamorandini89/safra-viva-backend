from . import db


class Talhao(db.Model):
    __tablename__ = 'talhao'
    id_talhao = db.Column(db.Integer, primary_key=True)

    # Dados Básicos
    nome_talhao = db.Column(db.String(200), nullable=False)
    codigo_talhao = db.Column(db.String(50), nullable=False)

    # Vinculação
    id_propriedade = db.Column(
        db.Integer,
        db.ForeignKey('propriedade.id_propriedade'),
        nullable=False
    )

    # Dados Físicos (em hectares)
    area_total = db.Column(db.Numeric(12, 2), nullable=False)
    area_utilizavel = db.Column(db.Numeric(12, 2), nullable=True)

    # Situação do talhão: Livre, Ocupado, Em preparo, etc.
    status_inicial = db.Column(db.String(30), nullable=True, default='Livre')

    # Características Técnicas
    id_tipo_solo = db.Column(db.Integer, db.ForeignKey('tipo_solo.id'), nullable=True)
    topografia = db.Column(db.String(50), nullable=True)
    observacoes = db.Column(db.String(500), nullable=True)

    # Coordenadas Geográficas
    latitude = db.Column(db.Numeric(11, 8), nullable=True)
    longitude = db.Column(db.Numeric(11, 8), nullable=True)

    # Controle
    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Talhao {self.nome_talhao}>"
