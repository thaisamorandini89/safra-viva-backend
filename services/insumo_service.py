from models import db
from models.atividade_insumo import AtividadeInsumo
from models.insumo import Insumo
from models.movimentacao_estoque import MovimentacaoEstoque
from models.produto import Produto
from models.propriedade import Propriedade
from models.categoria_insumo import CategoriaInsumo
from models.fabricante import Fabricante
from models.fornecedor import Fornecedor
from models.marca import Marca
from services.produto_service import ProdutoService


class InsumoService:
    @staticmethod
    def listar_todos():
        """
        Retorna a lista de todos os insumos (itens de estoque),
        incluindo os dados do produto e da categoria vinculados.
        """
        insumos = Insumo.query.order_by(Insumo.data_cadastro.desc()).all()
        resultado = []

        for ins in insumos:
            produto = Produto.query.get(ins.id_produto) if ins.id_produto else None

            categoria_nome = ""
            if produto and produto.id_categoria_insumo:
                cat = CategoriaInsumo.query.get(produto.id_categoria_insumo)
                if cat:
                    categoria_nome = cat.nome_categoria

            fabricante_nome = ""
            if produto and produto.id_fabricante:
                fab = Fabricante.query.get(produto.id_fabricante)
                if fab:
                    fabricante_nome = fab.nome_fabricante

            descricao_marca = ""
            if produto and produto.id_marca:
                mar = Marca.query.get(produto.id_marca)
                if mar:
                    descricao_marca = mar.descricao_marca

            fornecedor_nome = ""
            if produto and produto.id_fornecedor:
                forn = Fornecedor.query.get(produto.id_fornecedor)
                if forn:
                    fornecedor_nome = forn.nome_fantasia or forn.nome_fornecedor

            nome_propriedade = ""
            if ins.id_propriedade:
                prop = Propriedade.query.get(ins.id_propriedade)
                if prop:
                    nome_propriedade = prop.nome_propriedade

            resultado.append({
                "id_insumo": ins.id_insumo,
                "id_produto": ins.id_produto,
                "nome_produto": produto.nome_produto if produto else "",
                "id_categoria_insumo": produto.id_categoria_insumo if produto else None,
                "categoria_nome": categoria_nome,
                "subcategoria": produto.subcategoria if produto else None,
                "unidade_medida": produto.unidade_medida if produto else "",
                "id_fabricante": produto.id_fabricante if produto else None,
                "fabricante_nome": fabricante_nome,
                "id_marca": produto.id_marca if produto else None,
                "descricao_marca": descricao_marca,
                "id_fornecedor": produto.id_fornecedor if produto else None,
                "fornecedor_nome": fornecedor_nome,
                "registro_mapa": produto.registro_mapa if produto else None,
                "ficha_tecnica": produto.ficha_tecnica if produto else None,
                "observacoes": produto.observacoes if produto else None,
                "id_propriedade": ins.id_propriedade,
                "nome_propriedade": nome_propriedade,
                "estoque_atual": float(ins.estoque_atual) if ins.estoque_atual is not None else 0,
                "estoque_minimo": float(ins.estoque_minimo) if ins.estoque_minimo is not None else 0,
                "valor_unitario": float(ins.valor_unitario) if ins.valor_unitario is not None else 0,
                "status": ins.status,
                "data_cadastro": ins.data_cadastro.strftime("%Y-%m-%d %H:%M:%S") if ins.data_cadastro else None
            })

        return resultado

    @staticmethod
    def buscar_por_id(id_insumo):
        """
        Retorna um único insumo pelo seu id, no mesmo formato de listar_todos().
        """
        ins = Insumo.query.get(id_insumo)
        if not ins:
            raise ValueError("Insumo não encontrado.")

        for item in InsumoService.listar_todos():
            if item["id_insumo"] == ins.id_insumo:
                return item
        return None

    @staticmethod
    def _to_decimal(valor, campo):
        """Converte string/numero para float validando o campo."""
        if valor is None or valor == "":
            return None
        try:
            if isinstance(valor, str):
                valor = valor.strip().replace(".", "").replace(",", ".") if "," in valor else valor.strip()
            return float(valor)
        except (ValueError, TypeError):
            raise ValueError(f"O campo '{campo}' possui um valor numérico inválido.")

    @staticmethod
    def _validar_propriedade(id_propriedade):
        if not id_propriedade:
            return None
        if not Propriedade.query.get(id_propriedade):
            raise ValueError("Propriedade informada não foi encontrada.")
        return id_propriedade

    @staticmethod
    def criar_insumo(dados):
        """
        Cria um novo Insumo (item de estoque) vinculado a um Produto existente
        (`id_produto`) ou a um produto novo (`produto`), criado na mesma transação.
        """
        id_produto = dados.get("id_produto")
        dados_produto = dados.get("produto")
        if id_produto and dados_produto is not None:
            raise ValueError(
                "Informe um produto existente (id_produto) ou os dados de um "
                "produto novo (produto), não os dois."
            )

        if dados_produto is not None:
            if not isinstance(dados_produto, dict):
                raise ValueError("Os dados do produto são inválidos.")
            produto = ProdutoService.montar_produto(dados_produto)
        elif id_produto:
            produto = Produto.query.get(id_produto)
            if not produto:
                raise ValueError("Produto informado não foi encontrado.")
        else:
            raise ValueError("O produto vinculado é obrigatório.")

        id_propriedade = InsumoService._validar_propriedade(dados.get("id_propriedade"))
        estoque_atual = InsumoService._to_decimal(dados.get("estoque_atual"), "estoque_atual")
        estoque_minimo = InsumoService._to_decimal(dados.get("estoque_minimo"), "estoque_minimo")
        valor_unitario = InsumoService._to_decimal(dados.get("valor_unitario"), "valor_unitario")

        novo_insumo = Insumo(
            estoque_atual=estoque_atual if estoque_atual is not None else 0,
            estoque_minimo=estoque_minimo if estoque_minimo is not None else 0,
            valor_unitario=valor_unitario if valor_unitario is not None else 0,
            id_propriedade=id_propriedade,
            status=bool(dados["status"]) if dados.get("status") is not None else True,
        )

        try:
            if dados_produto is not None:
                db.session.add(produto)
                db.session.flush()
            novo_insumo.id_produto = produto.id_produto
            db.session.add(novo_insumo)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao salvar o insumo no banco de dados: {str(e)}")

        return novo_insumo

    @staticmethod
    def atualizar_insumo(id_insumo, dados):
        """
        Atualiza os dados de um Insumo existente.
        Apenas os campos enviados no payload são alterados.
        """
        ins = Insumo.query.get(id_insumo)
        if not ins:
            raise ValueError("Insumo não encontrado.")

        if "id_produto" in dados and dados.get("id_produto"):
            produto = Produto.query.get(dados.get("id_produto"))
            if not produto:
                raise ValueError("Produto informado não foi encontrado.")
            ins.id_produto = dados.get("id_produto")

        if dados.get("produto") is not None:
            if not isinstance(dados["produto"], dict):
                raise ValueError("Os dados do produto são inválidos.")
            ProdutoService.aplicar_alteracoes(Produto.query.get(ins.id_produto), dados["produto"])

        if "id_propriedade" in dados:
            ins.id_propriedade = InsumoService._validar_propriedade(dados.get("id_propriedade"))

        if "estoque_atual" in dados:
            ins.estoque_atual = InsumoService._to_decimal(dados.get("estoque_atual"), "estoque_atual")
        if "estoque_minimo" in dados:
            ins.estoque_minimo = InsumoService._to_decimal(dados.get("estoque_minimo"), "estoque_minimo")
        if "valor_unitario" in dados:
            ins.valor_unitario = InsumoService._to_decimal(dados.get("valor_unitario"), "valor_unitario")
        if "status" in dados:
            ins.status = bool(dados.get("status"))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar o insumo no banco de dados: {str(e)}")

        return ins

    @staticmethod
    def excluir_insumo(id_insumo):
        """
        Exclui um Insumo pelo seu id. O produto vinculado é mantido.
        """
        ins = Insumo.query.get(id_insumo)
        if not ins:
            raise ValueError("Insumo não encontrado.")

        em_uso = (
            MovimentacaoEstoque.query.filter_by(id_insumo=id_insumo).first()
            or AtividadeInsumo.query.filter_by(id_insumo=id_insumo).first()
        )
        if em_uso:
            raise ValueError(
                "O insumo está em uso por movimentações de estoque ou por "
                "atividades e não pode ser excluído."
            )

        db.session.delete(ins)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir o insumo no banco de dados: {str(e)}")

        return True
