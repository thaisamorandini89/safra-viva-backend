import uuid

from . import db


class Funcionario(db.Model):
    """Colaborador da empresa agrícola."""
    __tablename__ = 'funcionario'

    id_funcionario = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Dados Pessoais
    nome_completo = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    rg = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)

    # Dados Profissionais
    cargo = db.Column(db.String(100), nullable=False)
    data_admissao = db.Column(db.Date, nullable=False)
    data_desligamento = db.Column(db.Date, nullable=True)

    # Informações Adicionais
    observacoes = db.Column(db.String(500), nullable=True)

    # Controle
    status = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Funcionario {self.nome_completo}>"
