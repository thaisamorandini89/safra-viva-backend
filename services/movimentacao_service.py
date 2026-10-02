from decimal import Decimal

from models import db
from models.insumo import Insumo
from models.movimentacao_estoque import MovimentacaoEstoque
from models.produto import Produto
from models.responsavel import Responsavel


class MovimentacaoService:
    @staticmethod
    def registrar(dados):
        """
        Registra uma movimentação de estoque (ENTRADA/SAIDA) e atualiza o
        estoque_atual do insumo na mesma transação.
        `dados` deve ser um MovimentacaoCreate já validado pelo Pydantic.
        """
        # Lock pessimista para evitar corrida entre saídas simultâneas
        insumo = (
            Insumo.query
            .filter_by(id_insumo=dados.id_insumo)
            .with_for_update()
            .first()
        )
        if not insumo:
            raise ValueError("Insumo informado não foi encontrado.")

        if dados.id_responsavel is not None:
            if not Responsavel.query.get(dados.id_responsavel):
                raise ValueError("Responsável informado não foi encontrado.")

        quantidade = Decimal(dados.quantidade)
        saldo_atual = Decimal(insumo.estoque_atual or 0)

        if dados.tipo_movimentacao == 'ENTRADA':
            insumo.estoque_atual = saldo_atual + quantidade
        else:  # SAIDA
            if saldo_atual < quantidade:
                raise ValueError(
                    f"Saldo insuficiente para a saída: estoque atual é {saldo_atual}, "
                    f"quantidade solicitada é {quantidade}."
                )
            insumo.estoque_atual = saldo_atual - quantidade

        movimentacao = MovimentacaoEstoque(
            id_insumo=dados.id_insumo,
            tipo_movimentacao=dados.tipo_movimentacao,
            quantidade=quantidade,
            id_responsavel=dados.id_responsavel,
            observacao=dados.observacao
        )

        db.session.add(movimentacao)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao registrar a movimentação: {str(e)}")

        return movimentacao, insumo

    @staticmethod
    def listar(id_insumo=None):
        """
        Lista o histórico de movimentações (mais recentes primeiro),
        com filtro opcional por insumo.
        """
        query = MovimentacaoEstoque.query
        if id_insumo:
            query = query.filter_by(id_insumo=id_insumo)

        movimentacoes = query.order_by(MovimentacaoEstoque.data_movimentacao.desc()).all()
        resultado = []

        for mov in movimentacoes:
            insumo = Insumo.query.get(mov.id_insumo)
            produto = Produto.query.get(insumo.id_produto) if insumo else None
            responsavel = Responsavel.query.get(mov.id_responsavel) if mov.id_responsavel else None

            resultado.append({
                "id_movimentacao": mov.id_movimentacao,
                "id_insumo": mov.id_insumo,
                "nome_produto": produto.nome_produto if produto else "",
                "unidade_medida": produto.unidade_medida if produto else "",
                "tipo_movimentacao": mov.tipo_movimentacao,
                "quantidade": float(mov.quantidade),
                "data_movimentacao": mov.data_movimentacao.strftime("%Y-%m-%d %H:%M:%S") if mov.data_movimentacao else None,
                "id_responsavel": mov.id_responsavel,
                "responsavel_nome": responsavel.nome if responsavel else "",
                "observacao": mov.observacao
            })

        return resultado
