from models import db
from models.insumo import Insumo
from models.produto import Produto
from models.categoria_insumo import CategoriaInsumo


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

            resultado.append({
                "id_insumo": ins.id_insumo,
                "id_produto": ins.id_produto,
                "nome_produto": produto.nome_produto if produto else "",
                "id_categoria_insumo": produto.id_categoria_insumo if produto else None,
                "categoria_nome": categoria_nome,
                "unidade_medida": produto.unidade_medida if produto else "",
                "fabricante": produto.fabricante if produto else "",
                "marca": produto.marca if produto else "",
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
    def criar_insumo(dados):
        """
        Cria um novo Insumo (item de estoque) vinculado a um Produto.
        """
        id_produto = dados.get("id_produto")
        if not id_produto:
            raise ValueError("O produto vinculado é obrigatório.")

        produto = Produto.query.get(id_produto)
        if not produto:
            raise ValueError("Produto informado não foi encontrado.")

        estoque_atual = InsumoService._to_decimal(dados.get("estoque_atual"), "estoque_atual")
        estoque_minimo = InsumoService._to_decimal(dados.get("estoque_minimo"), "estoque_minimo")
        valor_unitario = InsumoService._to_decimal(dados.get("valor_unitario"), "valor_unitario")

        novo_insumo = Insumo(
            id_produto=id_produto,
            estoque_atual=estoque_atual if estoque_atual is not None else 0,
            estoque_minimo=estoque_minimo if estoque_minimo is not None else 0,
            valor_unitario=valor_unitario if valor_unitario is not None else 0
        )

        db.session.add(novo_insumo)
        try:
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
        Exclui um Insumo pelo seu id.
        """
        ins = Insumo.query.get(id_insumo)
        if not ins:
            raise ValueError("Insumo não encontrado.")

        db.session.delete(ins)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir o insumo no banco de dados: {str(e)}")

        return True
