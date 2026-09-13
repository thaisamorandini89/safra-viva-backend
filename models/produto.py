from . import db


class Produto(db.Model):
    __tablename__ = 'produto'
    id_produto = db.Column(db.Integer, primary_key=True)

    # Informações Básicas
    nome_produto = db.Column(db.String(200), nullable=False)
    id_categoria_insumo = db.Column(
        db.Integer,
        db.ForeignKey('categoria_insumo.id_categoria_insumo'),
        nullable=False
    )
    subcategoria = db.Column(db.String(100), nullable=True)  # Ex.: Fungicida, Herbicida, Ureia
    unidade_medida = db.Column(db.String(20), nullable=False)  # kg, L, t, sc, dose, etc.

    # Dados Comerciais (vinculados a cadastros próprios)
    id_fabricante = db.Column(db.Integer, db.ForeignKey('fabricante.id_fabricante'), nullable=True)
    id_fornecedor = db.Column(db.Integer, db.ForeignKey('fornecedor.id_fornecedor'), nullable=True)
    marca = db.Column(db.String(150), nullable=True)

    # Informações Complementares
    registro_mapa = db.Column(db.String(60), nullable=True)
    ficha_tecnica = db.Column(db.String(300), nullable=True)
    observacoes = db.Column(db.String(500), nullable=True)

    # Controle
    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Produto {self.nome_produto}>"
