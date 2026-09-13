from models import db
from models.produto import Produto
from models.categoria_insumo import CategoriaInsumo
from models.fabricante import Fabricante
from models.fornecedor import Fornecedor


class ProdutoService:
    @staticmethod
    def listar_todos():
        """
        Retorna a lista de todos os produtos cadastrados,
        incluindo o nome da categoria vinculada.
        """
        produtos = Produto.query.order_by(Produto.data_cadastro.desc()).all()
        resultado = []

        for prod in produtos:
            categoria_nome = ""
            if prod.id_categoria_insumo:
                cat = CategoriaInsumo.query.get(prod.id_categoria_insumo)
                if cat:
                    categoria_nome = cat.nome_categoria

            fabricante_nome = ""
            if prod.id_fabricante:
                fab = Fabricante.query.get(prod.id_fabricante)
                if fab:
                    fabricante_nome = fab.nome_fabricante

            fornecedor_nome = ""
            if prod.id_fornecedor:
                forn = Fornecedor.query.get(prod.id_fornecedor)
                if forn:
                    fornecedor_nome = forn.nome_fantasia or forn.nome_fornecedor

            resultado.append({
                "id_produto": prod.id_produto,
                "nome_produto": prod.nome_produto,
                "id_categoria_insumo": prod.id_categoria_insumo,
                "categoria_nome": categoria_nome,
                "subcategoria": prod.subcategoria,
                "unidade_medida": prod.unidade_medida,
                "id_fabricante": prod.id_fabricante,
                "fabricante_nome": fabricante_nome,
                "id_fornecedor": prod.id_fornecedor,
                "fornecedor_nome": fornecedor_nome,
                "marca": prod.marca,
                "registro_mapa": prod.registro_mapa,
                "ficha_tecnica": prod.ficha_tecnica,
                "observacoes": prod.observacoes,
                "status": prod.status,
                "data_cadastro": prod.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if prod.data_cadastro else None
            })

        return resultado

    @staticmethod
    def buscar_por_id(id_produto):
        """
        Retorna um único produto pelo seu id, no mesmo formato de listar_todos().
        """
        prod = Produto.query.get(id_produto)
        if not prod:
            raise ValueError("Produto não encontrado.")

        for item in ProdutoService.listar_todos():
            if item["id_produto"] == prod.id_produto:
                return item
        return None

    @staticmethod
    def criar_produto(dados):
        """
        Cria um novo Produto.
        """
        nome = dados.get("nome_produto")
        id_categoria = dados.get("id_categoria_insumo")
        unidade = dados.get("unidade_medida")

        if not nome or not str(nome).strip():
            raise ValueError("O nome do produto é obrigatório.")
        if not id_categoria:
            raise ValueError("A categoria do produto é obrigatória.")
        if not unidade or not str(unidade).strip():
            raise ValueError("A unidade de medida é obrigatória.")

        categoria = CategoriaInsumo.query.get(id_categoria)
        if not categoria:
            raise ValueError("Categoria de insumo informada não foi encontrada.")

        # Validar fabricante e fornecedor (opcionais)
        id_fabricante = dados.get("id_fabricante") or None
        if id_fabricante and not Fabricante.query.get(id_fabricante):
            raise ValueError("Fabricante informado não foi encontrado.")
        id_fornecedor = dados.get("id_fornecedor") or None
        if id_fornecedor and not Fornecedor.query.get(id_fornecedor):
            raise ValueError("Fornecedor informado não foi encontrado.")

        novo_produto = Produto(
            nome_produto=nome.strip(),
            id_categoria_insumo=id_categoria,
            subcategoria=(dados.get("subcategoria") or "").strip() or None,
            unidade_medida=unidade.strip(),
            id_fabricante=id_fabricante,
            id_fornecedor=id_fornecedor,
            marca=(dados.get("marca") or "").strip() or None,
            registro_mapa=(dados.get("registro_mapa") or "").strip() or None,
            ficha_tecnica=(dados.get("ficha_tecnica") or "").strip() or None,
            observacoes=(dados.get("observacoes") or "").strip() or None
        )

        db.session.add(novo_produto)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o produto no banco de dados: {str(e)}")

        return novo_produto

    @staticmethod
    def atualizar_produto(id_produto, dados):
        """
        Atualiza os dados de um Produto existente.
        Apenas os campos enviados no payload são alterados.
        """
        prod = Produto.query.get(id_produto)
        if not prod:
            raise ValueError("Produto não encontrado.")

        if "nome_produto" in dados:
            nome = (dados.get("nome_produto") or "").strip()
            if not nome:
                raise ValueError("O nome do produto não pode ficar vazio.")
            prod.nome_produto = nome

        if "id_categoria_insumo" in dados and dados.get("id_categoria_insumo"):
            categoria = CategoriaInsumo.query.get(dados.get("id_categoria_insumo"))
            if not categoria:
                raise ValueError("Categoria de insumo informada não foi encontrada.")
            prod.id_categoria_insumo = dados.get("id_categoria_insumo")

        if "unidade_medida" in dados:
            unidade = (dados.get("unidade_medida") or "").strip()
            if not unidade:
                raise ValueError("A unidade de medida não pode ficar vazia.")
            prod.unidade_medida = unidade

        if "subcategoria" in dados:
            prod.subcategoria = (dados.get("subcategoria") or "").strip() or None
        if "id_fabricante" in dados:
            id_fab = dados.get("id_fabricante") or None
            if id_fab and not Fabricante.query.get(id_fab):
                raise ValueError("Fabricante informado não foi encontrado.")
            prod.id_fabricante = id_fab
        if "id_fornecedor" in dados:
            id_forn = dados.get("id_fornecedor") or None
            if id_forn and not Fornecedor.query.get(id_forn):
                raise ValueError("Fornecedor informado não foi encontrado.")
            prod.id_fornecedor = id_forn
        if "marca" in dados:
            prod.marca = (dados.get("marca") or "").strip() or None
        if "registro_mapa" in dados:
            prod.registro_mapa = (dados.get("registro_mapa") or "").strip() or None
        if "ficha_tecnica" in dados:
            prod.ficha_tecnica = (dados.get("ficha_tecnica") or "").strip() or None
        if "observacoes" in dados:
            prod.observacoes = (dados.get("observacoes") or "").strip() or None
        if "status" in dados:
            prod.status = bool(dados.get("status"))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar o produto no banco de dados: {str(e)}")

        return prod

    @staticmethod
    def excluir_produto(id_produto):
        """
        Exclui um Produto pelo seu id.
        """
        prod = Produto.query.get(id_produto)
        if not prod:
            raise ValueError("Produto não encontrado.")

        db.session.delete(prod)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir o produto no banco de dados: {str(e)}")

        return True
