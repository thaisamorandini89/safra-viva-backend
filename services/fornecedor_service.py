from models import db
from models.fornecedor import Fornecedor


class FornecedorService:
    @staticmethod
    def listar_todos():
        fornecedores = Fornecedor.query.order_by(Fornecedor.nome_fornecedor.asc()).all()
        return [{
            "id_fornecedor": f.id_fornecedor,
            "nome_fornecedor": f.nome_fornecedor,
            "nome_fantasia": f.nome_fantasia,
            "cnpj": f.cnpj,
            "telefone": f.telefone,
            "email": f.email,
            "id_logradouro": f.id_logradouro,
            "observacoes": f.observacoes,
            "status": f.status,
            "data_cadastro": f.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if f.data_cadastro else None
        } for f in fornecedores]

    @staticmethod
    def buscar_por_id(id_fornecedor):
        f = Fornecedor.query.get(id_fornecedor)
        if not f:
            raise ValueError("Fornecedor não encontrado.")
        for item in FornecedorService.listar_todos():
            if item["id_fornecedor"] == f.id_fornecedor:
                return item
        return None

    @staticmethod
    def criar_fornecedor(dados):
        nome = dados.get("nome_fornecedor")
        if not nome or not str(nome).strip():
            raise ValueError("O nome do fornecedor é obrigatório.")

        novo = Fornecedor(
            nome_fornecedor=nome.strip(),
            nome_fantasia=(dados.get("nome_fantasia") or "").strip() or None,
            cnpj=''.join(filter(str.isdigit, str(dados.get("cnpj") or ""))) or None,
            telefone=(dados.get("telefone") or "").strip() or None,
            email=(dados.get("email") or "").strip() or None,
            id_logradouro=dados.get("id_logradouro") or None,
            observacoes=(dados.get("observacoes") or "").strip() or None
        )
        db.session.add(novo)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o fornecedor no banco de dados: {str(e)}")
        return novo

    @staticmethod
    def atualizar_fornecedor(id_fornecedor, dados):
        f = Fornecedor.query.get(id_fornecedor)
        if not f:
            raise ValueError("Fornecedor não encontrado.")

        if "nome_fornecedor" in dados:
            nome = (dados.get("nome_fornecedor") or "").strip()
            if not nome:
                raise ValueError("O nome do fornecedor não pode ficar vazio.")
            f.nome_fornecedor = nome
        if "nome_fantasia" in dados:
            f.nome_fantasia = (dados.get("nome_fantasia") or "").strip() or None
        if "cnpj" in dados:
            f.cnpj = ''.join(filter(str.isdigit, str(dados.get("cnpj") or ""))) or None
        if "telefone" in dados:
            f.telefone = (dados.get("telefone") or "").strip() or None
        if "email" in dados:
            f.email = (dados.get("email") or "").strip() or None
        if "id_logradouro" in dados:
            f.id_logradouro = dados.get("id_logradouro") or None
        if "observacoes" in dados:
            f.observacoes = (dados.get("observacoes") or "").strip() or None
        if "status" in dados:
            f.status = bool(dados.get("status"))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar o fornecedor no banco de dados: {str(e)}")
        return f

    @staticmethod
    def excluir_fornecedor(id_fornecedor):
        f = Fornecedor.query.get(id_fornecedor)
        if not f:
            raise ValueError("Fornecedor não encontrado.")
        db.session.delete(f)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir o fornecedor no banco de dados: {str(e)}")
        return True
