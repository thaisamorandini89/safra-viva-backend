from models import db
from models.tipo_atividade import TipoAtividade
from models.categoria_atividade import CategoriaAtividade


class TipoAtividadeService:
    @staticmethod
    def _serializar(t):
        return {
            "id_atividade": t.id_atividade,
            "descricao": t.descricao,
            "id_categoria_atividade": t.id_categoria_atividade,
            "categoria_nome": t.categoria.nome if t.categoria else None,
            "status": t.status,
        }

    @staticmethod
    def listar_todos(id_categoria_atividade=None):
        query = TipoAtividade.query
        if id_categoria_atividade:
            query = query.filter_by(id_categoria_atividade=id_categoria_atividade)
        tipos = query.order_by(TipoAtividade.descricao.asc()).all()
        return [TipoAtividadeService._serializar(t) for t in tipos]

    @staticmethod
    def buscar_por_id(id_atividade):
        t = TipoAtividade.query.get(id_atividade)
        if not t:
            raise ValueError("Tipo de atividade não encontrado.")
        return TipoAtividadeService._serializar(t)

    @staticmethod
    def criar(dados):
        descricao = (dados.get("descricao") or "").strip()
        if not descricao:
            raise ValueError("A descrição do tipo de atividade é obrigatória.")
        id_cat = dados.get("id_categoria_atividade")
        if not id_cat:
            raise ValueError("A categoria do tipo de atividade é obrigatória.")
        if not CategoriaAtividade.query.get(id_cat):
            raise ValueError("Categoria de atividade não encontrada.")
        novo = TipoAtividade(
            descricao=descricao,
            id_categoria_atividade=id_cat,
            status=bool(dados.get("status", True)),
        )
        db.session.add(novo)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o tipo de atividade: {str(e)}")
        return novo

    @staticmethod
    def atualizar(id_atividade, dados):
        t = TipoAtividade.query.get(id_atividade)
        if not t:
            raise ValueError("Tipo de atividade não encontrado.")
        if "descricao" in dados:
            descricao = (dados.get("descricao") or "").strip()
            if not descricao:
                raise ValueError("A descrição não pode ficar vazia.")
            t.descricao = descricao
        if "id_categoria_atividade" in dados:
            id_cat = dados.get("id_categoria_atividade")
            if not CategoriaAtividade.query.get(id_cat):
                raise ValueError("Categoria de atividade não encontrada.")
            t.id_categoria_atividade = id_cat
        if "status" in dados:
            t.status = bool(dados.get("status"))
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar o tipo de atividade: {str(e)}")
        return t

    @staticmethod
    def excluir(id_atividade):
        t = TipoAtividade.query.get(id_atividade)
        if not t:
            raise ValueError("Tipo de atividade não encontrado.")
        db.session.delete(t)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir o tipo de atividade: {str(e)}")
        return True
