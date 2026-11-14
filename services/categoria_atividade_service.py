from models import db
from models.categoria_atividade import CategoriaAtividade


class CategoriaAtividadeService:
    @staticmethod
    def _serializar(cat):
        return {
            "id_categoria_atividade": cat.id_categoria_atividade,
            "nome": cat.nome,
            "status": cat.status,
        }

    @staticmethod
    def listar_todas():
        cats = CategoriaAtividade.query.order_by(CategoriaAtividade.nome.asc()).all()
        return [CategoriaAtividadeService._serializar(c) for c in cats]

    @staticmethod
    def buscar_por_id(id_categoria_atividade):
        cat = CategoriaAtividade.query.get(id_categoria_atividade)
        if not cat:
            raise ValueError("Categoria de atividade não encontrada.")
        return CategoriaAtividadeService._serializar(cat)

    @staticmethod
    def criar(dados):
        nome = (dados.get("nome") or "").strip()
        if not nome:
            raise ValueError("O nome da categoria é obrigatório.")
        if CategoriaAtividade.query.filter_by(nome=nome).first():
            raise ValueError("Já existe uma categoria de atividade com este nome.")
        nova = CategoriaAtividade(nome=nome, status=bool(dados.get("status", True)))
        db.session.add(nova)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar a categoria: {str(e)}")
        return nova

    @staticmethod
    def atualizar(id_categoria_atividade, dados):
        cat = CategoriaAtividade.query.get(id_categoria_atividade)
        if not cat:
            raise ValueError("Categoria de atividade não encontrada.")
        if "nome" in dados:
            nome = (dados.get("nome") or "").strip()
            if not nome:
                raise ValueError("O nome da categoria não pode ficar vazio.")
            existente = CategoriaAtividade.query.filter_by(nome=nome).first()
            if existente and existente.id_categoria_atividade != cat.id_categoria_atividade:
                raise ValueError("Já existe uma categoria de atividade com este nome.")
            cat.nome = nome
        if "status" in dados:
            cat.status = bool(dados.get("status"))
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar a categoria: {str(e)}")
        return cat

    @staticmethod
    def excluir(id_categoria_atividade):
        cat = CategoriaAtividade.query.get(id_categoria_atividade)
        if not cat:
            raise ValueError("Categoria de atividade não encontrada.")
        db.session.delete(cat)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir a categoria: {str(e)}")
        return True
