from models import db
from models.categoria_insumo import CategoriaInsumo


class CategoriaInsumoService:
    @staticmethod
    def listar_todas():
        """
        Retorna a lista de todas as categorias de insumo cadastradas.
        """
        categorias = CategoriaInsumo.query.order_by(CategoriaInsumo.nome_categoria.asc()).all()
        resultado = []

        for cat in categorias:
            resultado.append({
                "id_categoria_insumo": cat.id_categoria_insumo,
                "nome_categoria": cat.nome_categoria,
                "descricao": cat.descricao,
                "status": cat.status,
                "data_cadastro": cat.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if cat.data_cadastro else None
            })

        return resultado

    @staticmethod
    def buscar_por_id(id_categoria_insumo):
        """
        Retorna uma única categoria pelo seu id.
        """
        cat = CategoriaInsumo.query.get(id_categoria_insumo)
        if not cat:
            raise ValueError("Categoria de insumo não encontrada.")

        return {
            "id_categoria_insumo": cat.id_categoria_insumo,
            "nome_categoria": cat.nome_categoria,
            "descricao": cat.descricao,
            "status": cat.status,
            "data_cadastro": cat.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if cat.data_cadastro else None
        }

    @staticmethod
    def criar_categoria(dados):
        """
        Cria uma nova Categoria de Insumo.
        """
        nome = dados.get("nome_categoria")
        if not nome or not str(nome).strip():
            raise ValueError("O nome da categoria é obrigatório.")

        # Evita duplicidade
        existente = CategoriaInsumo.query.filter_by(nome_categoria=nome.strip()).first()
        if existente:
            raise ValueError("Já existe uma categoria cadastrada com este nome.")

        nova_categoria = CategoriaInsumo(
            nome_categoria=nome.strip(),
            descricao=(dados.get("descricao") or "").strip() or None
        )

        db.session.add(nova_categoria)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar a categoria no banco de dados: {str(e)}")

        return nova_categoria

    @staticmethod
    def atualizar_categoria(id_categoria_insumo, dados):
        """
        Atualiza os dados de uma Categoria de Insumo existente.
        Apenas os campos enviados no payload são alterados.
        """
        cat = CategoriaInsumo.query.get(id_categoria_insumo)
        if not cat:
            raise ValueError("Categoria de insumo não encontrada.")

        if "nome_categoria" in dados:
            nome = (dados.get("nome_categoria") or "").strip()
            if not nome:
                raise ValueError("O nome da categoria não pode ficar vazio.")
            cat.nome_categoria = nome

        if "descricao" in dados:
            cat.descricao = (dados.get("descricao") or "").strip() or None

        if "status" in dados:
            cat.status = bool(dados.get("status"))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar a categoria no banco de dados: {str(e)}")

        return cat

    @staticmethod
    def excluir_categoria(id_categoria_insumo):
        """
        Exclui uma Categoria de Insumo pelo seu id.
        """
        cat = CategoriaInsumo.query.get(id_categoria_insumo)
        if not cat:
            raise ValueError("Categoria de insumo não encontrada.")

        db.session.delete(cat)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir a categoria no banco de dados: {str(e)}")

        return True
