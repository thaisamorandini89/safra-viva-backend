from . import db


class CategoriaInsumo(db.Model):
    __tablename__ = 'categoria_insumo'
    id_categoria_insumo = db.Column(db.Integer, primary_key=True)
    nome_categoria = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(300), nullable=True)

    # Controle
    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<CategoriaInsumo {self.nome_categoria}>"
