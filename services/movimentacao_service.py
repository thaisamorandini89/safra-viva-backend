from decimal import Decimal

from models import db
from models.atividade import Atividade
from models.fornecedor import Fornecedor
from models.funcionario import Funcionario
from models.insumo import Insumo
from models.movimentacao_estoque import MovimentacaoEstoque
from models.produto import Produto
from models.talhao import Talhao


class MovimentacaoService:
    @staticmethod
    def registrar(dados):
        """
        Registra uma movimentacao de estoque (ENTRADA/SAIDA) e atualiza o
        estoque_atual do insumo na mesma transacao.
        `dados` deve ser um MovimentacaoCreate ja validado pelo Pydantic.
        """
        insumo = (
            Insumo.query
            .filter_by(id_insumo=dados.id_insumo)
            .with_for_update()
            .first()
        )
        if not insumo:
            raise ValueError("Insumo informado nao foi encontrado.")

        if dados.id_funcionario is not None:
            if not Funcionario.query.get(dados.id_funcionario):
                raise ValueError("Funcionario informado nao foi encontrado.")

        if dados.id_fornecedor is not None:
            if not Fornecedor.query.get(dados.id_fornecedor):
                raise ValueError("Fornecedor informado nao foi encontrado.")

        if dados.id_talhao is not None:
            if not Talhao.query.get(dados.id_talhao):
                raise ValueError("Talhao informado nao foi encontrado.")

        if dados.id_atividade is not None:
            if not Atividade.query.get(dados.id_atividade):
                raise ValueError("Atividade informada nao foi encontrada.")

        quantidade = Decimal(dados.quantidade)
        saldo_atual = Decimal(insumo.estoque_atual or 0)

        if dados.tipo_movimentacao == 'ENTRADA':
            insumo.estoque_atual = saldo_atual + quantidade
        else:
            if saldo_atual < quantidade:
                raise ValueError(
                    f"Saldo insuficiente para a saida: estoque atual e {saldo_atual}, "
                    f"quantidade solicitada e {quantidade}."
                )
            insumo.estoque_atual = saldo_atual - quantidade

        movimentacao = MovimentacaoEstoque(
            id_insumo=dados.id_insumo,
            tipo_movimentacao=dados.tipo_movimentacao,
            quantidade=quantidade,
            valor_unitario=dados.valor_unitario,
            id_funcionario=dados.id_funcionario,
            observacao=dados.observacao,
            id_fornecedor=dados.id_fornecedor,
            numero_nota_fiscal=dados.numero_nota_fiscal,
            numero_lote=dados.numero_lote,
            data_fabricacao=dados.data_fabricacao,
            data_validade=dados.data_validade,
            id_talhao=dados.id_talhao,
            safra=dados.safra,
            id_atividade=dados.id_atividade,
            destino_finalidade=dados.destino_finalidade,
        )

        db.session.add(movimentacao)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao registrar a movimentacao: {str(e)}")

        return movimentacao, insumo

    @staticmethod
    def serializar(mov, estoque_atual=None):
        """Serializa a movimentacao resolvendo os nomes das entidades vinculadas."""
        insumo = Insumo.query.get(mov.id_insumo)
        produto = Produto.query.get(insumo.id_produto) if insumo else None
        funcionario = Funcionario.query.get(mov.id_funcionario) if mov.id_funcionario else None
        fornecedor = Fornecedor.query.get(mov.id_fornecedor) if mov.id_fornecedor else None
        talhao = Talhao.query.get(mov.id_talhao) if mov.id_talhao else None
        atividade = Atividade.query.get(mov.id_atividade) if mov.id_atividade else None

        dados = {
            "id_movimentacao": mov.id_movimentacao,
            "id_insumo": mov.id_insumo,
            "nome_produto": produto.nome_produto if produto else "",
            "unidade_medida": produto.unidade_medida if produto else "",
            "tipo_movimentacao": mov.tipo_movimentacao,
            "quantidade": float(mov.quantidade),
            "valor_unitario": float(mov.valor_unitario) if mov.valor_unitario is not None else None,
            "data_movimentacao": mov.data_movimentacao.strftime("%Y-%m-%d %H:%M:%S") if mov.data_movimentacao else None,
            "id_funcionario": mov.id_funcionario,
            "funcionario_nome": funcionario.nome_completo if funcionario else "",
            "observacao": mov.observacao,
            "id_fornecedor": mov.id_fornecedor,
            "fornecedor_nome": (fornecedor.nome_fantasia or fornecedor.nome_fornecedor) if fornecedor else "",
            "numero_nota_fiscal": mov.numero_nota_fiscal,
            "numero_lote": mov.numero_lote,
            "data_fabricacao": mov.data_fabricacao.strftime("%Y-%m-%d") if mov.data_fabricacao else None,
            "data_validade": mov.data_validade.strftime("%Y-%m-%d") if mov.data_validade else None,
            "id_talhao": mov.id_talhao,
            "nome_talhao": talhao.nome_talhao if talhao else "",
            "safra": mov.safra,
            "id_atividade": mov.id_atividade,
            "atividade_descricao": atividade.descricao if atividade else "",
            "destino_finalidade": mov.destino_finalidade,
        }

        if estoque_atual is not None:
            dados["estoque_atual"] = float(estoque_atual)

        return dados

    @staticmethod
    def listar(id_insumo=None):
        """
        Lista o historico de movimentacoes (mais recentes primeiro),
        com filtro opcional por insumo.
        """
        query = MovimentacaoEstoque.query
        if id_insumo:
            query = query.filter_by(id_insumo=id_insumo)

        movimentacoes = query.order_by(MovimentacaoEstoque.data_movimentacao.desc()).all()
        return [MovimentacaoService.serializar(mov) for mov in movimentacoes]
