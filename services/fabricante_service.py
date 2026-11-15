from sqlalchemy import func

from models import db
from models.fabricante import Fabricante
from models.produto import Produto
from utils.documentos import cnpj_digitos


class FabricanteService:
    @staticmethod
    def _validar_nome(nome, id_fabricante=None):
        nome = (nome or "").strip()
        repetido = Fabricante.query.filter(
            func.lower(Fabricante.nome_fabricante) == nome.lower(),
            Fabricante.id_fabricante != id_fabricante,
        ).first()
        if repetido:
            raise ValueError("Já existe um fabricante com este nome.")
        return nome

    @staticmethod
    def listar_todos():
        fabricantes = Fabricante.query.order_by(Fabricante.nome_fabricante.asc()).all()
        return [{
            "id_fabricante": f.id_fabricante,
            "nome_fabricante": f.nome_fabricante,
            "cnpj": f.cnpj,
            "telefone": f.telefone,
            "email": f.email,
            "website": f.website,
            "observacoes": f.observacoes,
            "status": f.status,
            "data_cadastro": f.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if f.data_cadastro else None
        } for f in fabricantes]

    @staticmethod
    def buscar_por_id(id_fabricante):
        f = Fabricante.query.get(id_fabricante)
        if not f:
            raise LookupError("Fabricante não encontrado.")
        for item in FabricanteService.listar_todos():
            if item["id_fabricante"] == f.id_fabricante:
                return item
        return None

    @staticmethod
    def criar_fabricante(dados):
        nome = dados.get("nome_fabricante")
        if not nome or not str(nome).strip():
            raise ValueError("O nome do fabricante é obrigatório.")

        novo = Fabricante(
            nome_fabricante=FabricanteService._validar_nome(nome),
            cnpj=cnpj_digitos(dados.get("cnpj")),
            telefone=(dados.get("telefone") or "").strip() or None,
            email=(dados.get("email") or "").strip() or None,
            website=(dados.get("website") or "").strip() or None,
            observacoes=(dados.get("observacoes") or "").strip() or None
        )
        db.session.add(novo)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o fabricante no banco de dados: {str(e)}")
        return novo

    @staticmethod
    def atualizar_fabricante(id_fabricante, dados):
        f = Fabricante.query.get(id_fabricante)
        if not f:
            raise LookupError("Fabricante não encontrado.")

        if "nome_fabricante" in dados:
            nome = (dados.get("nome_fabricante") or "").strip()
            if not nome:
                raise ValueError("O nome do fabricante não pode ficar vazio.")
            f.nome_fabricante = FabricanteService._validar_nome(nome, id_fabricante)
        if "cnpj" in dados:
            f.cnpj = cnpj_digitos(dados.get("cnpj"))
        if "telefone" in dados:
            f.telefone = (dados.get("telefone") or "").strip() or None
        if "email" in dados:
            f.email = (dados.get("email") or "").strip() or None
        if "website" in dados:
            f.website = (dados.get("website") or "").strip() or None
        if "observacoes" in dados:
            f.observacoes = (dados.get("observacoes") or "").strip() or None
        if "status" in dados:
            f.status = bool(dados.get("status"))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar o fabricante no banco de dados: {str(e)}")
        return f

    @staticmethod
    def excluir_fabricante(id_fabricante):
        f = Fabricante.query.get(id_fabricante)
        if not f:
            raise LookupError("Fabricante não encontrado.")
        if Produto.query.filter_by(id_fabricante=id_fabricante).first():
            raise ValueError(
                "O fabricante está em uso por produtos e não pode ser excluído. "
                "Inative-o se não for mais usar."
            )
        db.session.delete(f)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir o fabricante no banco de dados: {str(e)}")
        return True
