from . import db


class Usuario(db.Model):
    """Usuário do sistema, com perfil de acesso e empresa de escopo."""
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(40), nullable=False)
    id_empresa = db.Column(
        db.Integer,
        db.ForeignKey('empresa_agricola.id_empresa'),
        nullable=True
    )
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Usuario {self.email} perfil={self.perfil}>"
