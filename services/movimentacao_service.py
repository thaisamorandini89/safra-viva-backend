from datetime import datetime
from decimal import Decimal

from models import db
from models.atividade_agricola import AtividadeAgricola
from models.tipo_atividade import TipoAtividade as Atividade
from models.fornecedor import Fornecedor
from models.funcionario import Funcionario
from models.insumo import Insumo
from models.lote_insumo import LoteInsumo
from models.movimentacao_estoque import MovimentacaoEstoque
from models.movimentacao_lote import MovimentacaoLote
from models.produto import Produto
from models.talhao import Talhao
from utils.datas import hoje


def _qtd(valor):
    """Quantidade sem zeros a direita, para as mensagens de erro."""
    return format(Decimal(valor).normalize(), "f")


class MovimentacaoService:
    @staticmethod
    def saldo_utilizavel(insumo):
        """Estoque do insumo menos o saldo dos lotes vencidos."""
        vencido = (
            db.session.query(db.func.coalesce(db.func.sum(LoteInsumo.quantidade), 0))
            .filter(LoteInsumo.id_insumo == insumo.id_insumo, LoteInsumo.data_validade < hoje())
            .scalar()
        )
        return Decimal(insumo.estoque_atual or 0) - Decimal(vencido)

    @staticmethod
    def _entrada_no_lote(insumo, dados, quantidade):
        """Cria o lote da entrada ou soma ao existente; devolve [(lote, quantidade)]."""
        if not dados.numero_lote:
            return []

        lote = LoteInsumo.query.filter_by(
            id_insumo=insumo.id_insumo, numero_lote=dados.numero_lote
        ).first()
        if lote is None:
            lote = LoteInsumo(
                id_insumo=insumo.id_insumo,
                numero_lote=dados.numero_lote,
                data_fabricacao=dados.data_fabricacao,
                data_validade=dados.data_validade,
                quantidade=0,
            )
            db.session.add(lote)
        elif dados.data_validade is not None:
            if lote.data_validade is None:
                lote.data_validade = dados.data_validade
            elif lote.data_validade != dados.data_validade:
                raise ValueError(
                    f"O lote {lote.numero_lote} ja esta registrado com validade "
                    f"{lote.data_validade.strftime('%d/%m/%Y')}. Confira a validade "
                    "ou use outro numero de lote."
                )

        lote.quantidade = Decimal(lote.quantidade or 0) + quantidade
        return [(lote, quantidade)]

    @staticmethod
    def _saida_dos_lotes(insumo, dados, quantidade, saldo_atual):
        """Retira a saida dos lotes do insumo; devolve [(lote, quantidade)]."""
        if dados.id_lote is not None:
            lote = LoteInsumo.query.get(dados.id_lote)
            if not lote or lote.id_insumo != insumo.id_insumo:
                raise ValueError("O lote informado nao pertence ao insumo.")
            saldo_lote = Decimal(lote.quantidade or 0)
            if quantidade > saldo_lote:
                raise ValueError(
                    f"Saldo insuficiente no lote {lote.numero_lote}: saldo do lote e "
                    f"{_qtd(saldo_lote)}, quantidade solicitada e {_qtd(quantidade)}."
                )
            if quantidade > saldo_atual:
                raise ValueError(
                    f"Saldo insuficiente para a saida: estoque atual e {_qtd(saldo_atual)}, "
                    f"quantidade solicitada e {_qtd(quantidade)}."
                )
            lote.quantidade = saldo_lote - quantidade
            return [(lote, quantidade)]

        hoje_local = hoje()
        lotes = (
            LoteInsumo.query
            .filter(LoteInsumo.id_insumo == insumo.id_insumo, LoteInsumo.quantidade > 0)
            .all()
        )
        vencidos = [l for l in lotes if l.data_validade and l.data_validade < hoje_local]
        utilizavel = MovimentacaoService.saldo_utilizavel(insumo)
        vencido = saldo_atual - utilizavel

        if quantidade > utilizavel:
            if vencido > 0:
                raise ValueError(
                    f"Saldo utilizavel insuficiente para a saida: saldo utilizavel e "
                    f"{_qtd(utilizavel)} ({_qtd(vencido)} em lotes vencidos, que so saem por "
                    f"descarte do lote), quantidade solicitada e {_qtd(quantidade)}."
                )
            raise ValueError(
                f"Saldo insuficiente para a saida: estoque atual e {_qtd(saldo_atual)}, "
                f"quantidade solicitada e {_qtd(quantidade)}."
            )

        # validade mais proxima primeiro, lotes sem validade depois; o que sobrar sai do saldo sem lote
        validos = sorted(
            (l for l in lotes if l not in vencidos),
            key=lambda l: (l.data_validade is None, l.data_validade or hoje_local, l.id_lote),
        )
        afetados = []
        restante = quantidade
        for lote in validos:
            if restante <= 0:
                break
            retirado = min(Decimal(lote.quantidade), restante)
            lote.quantidade = Decimal(lote.quantidade) - retirado
            afetados.append((lote, retirado))
            restante -= retirado
        return afetados

    @staticmethod
    def _lotes_da_movimentacao(id_movimentacao):
        linhas = (
            db.session.query(MovimentacaoLote, LoteInsumo)
            .join(LoteInsumo, LoteInsumo.id_lote == MovimentacaoLote.id_lote)
            .filter(MovimentacaoLote.id_movimentacao == id_movimentacao)
            .order_by(MovimentacaoLote.id)
            .all()
        )
        return [
            {
                "id_lote": lote.id_lote,
                "numero_lote": lote.numero_lote,
                "data_validade": lote.data_validade.strftime("%Y-%m-%d") if lote.data_validade else None,
                "quantidade": float(ligacao.quantidade),
            }
            for ligacao, lote in linhas
        ]

    @staticmethod
    def aplicar(dados, origem='MANUAL'):
        """
        Aplica uma movimentacao de estoque (saldo, lotes e registro) na
        transacao corrente, sem commit.
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

        id_atividade = dados.id_atividade
        if dados.id_atividade_agricola is not None:
            operacao = AtividadeAgricola.query.get(dados.id_atividade_agricola)
            if not operacao:
                raise ValueError("Atividade agricola informada nao foi encontrada.")
            if id_atividade is not None and id_atividade != operacao.id_tipo_atividade:
                raise ValueError(
                    "O tipo de atividade informado nao corresponde ao da atividade agricola."
                )
            if dados.id_talhao is not None and dados.id_talhao != operacao.id_talhao:
                raise ValueError(
                    "O talhao informado nao corresponde ao da atividade agricola."
                )
            id_atividade = operacao.id_tipo_atividade

        quantidade = Decimal(dados.quantidade)
        saldo_atual = Decimal(insumo.estoque_atual or 0)

        if dados.tipo_movimentacao == 'ENTRADA':
            lotes_afetados = MovimentacaoService._entrada_no_lote(insumo, dados, quantidade)
            insumo.estoque_atual = saldo_atual + quantidade
        else:
            lotes_afetados = MovimentacaoService._saida_dos_lotes(
                insumo, dados, quantidade, saldo_atual
            )
            insumo.estoque_atual = saldo_atual - quantidade

        movimentacao = MovimentacaoEstoque(
            id_insumo=dados.id_insumo,
            tipo_movimentacao=dados.tipo_movimentacao,
            origem=origem,
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
            id_atividade=id_atividade,
            id_atividade_agricola=dados.id_atividade_agricola,
            destino_finalidade=dados.destino_finalidade,
        )
        if dados.data_movimentacao is not None:
            # a coluna guarda hora UTC (padrao do banco); mantem a ordem dentro do dia
            movimentacao.data_movimentacao = datetime.combine(
                dados.data_movimentacao, datetime.utcnow().time()
            )

        db.session.add(movimentacao)
        db.session.flush()
        for lote, quantidade_lote in lotes_afetados:
            db.session.add(MovimentacaoLote(
                id_movimentacao=movimentacao.id_movimentacao,
                id_lote=lote.id_lote,
                quantidade=quantidade_lote,
            ))

        return movimentacao, insumo

    @staticmethod
    def desfazer(movimentacao):
        """
        Desfaz uma saida na transacao corrente, sem commit: devolve a quantidade
        ao estoque e aos lotes de onde saiu e apaga a movimentacao.
        """
        insumo = (
            Insumo.query
            .filter_by(id_insumo=movimentacao.id_insumo)
            .with_for_update()
            .first()
        )
        insumo.estoque_atual = Decimal(insumo.estoque_atual or 0) + Decimal(movimentacao.quantidade)

        ligacoes = MovimentacaoLote.query.filter_by(
            id_movimentacao=movimentacao.id_movimentacao
        ).all()
        for ligacao in ligacoes:
            lote = LoteInsumo.query.get(ligacao.id_lote)
            lote.quantidade = Decimal(lote.quantidade or 0) + Decimal(ligacao.quantidade)
            db.session.delete(ligacao)

        db.session.delete(movimentacao)

    @staticmethod
    def registrar(dados):
        """
        Registra uma movimentacao lancada pela API (origem MANUAL) e confirma
        a transacao.
        """
        try:
            movimentacao, insumo = MovimentacaoService.aplicar(dados)
            db.session.commit()
        except ValueError:
            db.session.rollback()
            raise
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
            "origem": mov.origem,
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
            "codigo_talhao": talhao.codigo_talhao if talhao else None,
            "safra": mov.safra,
            "id_atividade": mov.id_atividade,
            "id_atividade_agricola": mov.id_atividade_agricola,
            "atividade_descricao": atividade.descricao if atividade else "",
            "destino_finalidade": mov.destino_finalidade,
            "lotes": MovimentacaoService._lotes_da_movimentacao(mov.id_movimentacao),
        }

        if estoque_atual is not None:
            dados["estoque_atual"] = float(estoque_atual)

        return dados

    @staticmethod
    def listar(id_insumo=None, id_atividade_agricola=None):
        """
        Lista o historico de movimentacoes (mais recentes primeiro),
        com filtros opcionais por insumo e por atividade agricola.
        """
        query = MovimentacaoEstoque.query
        if id_insumo:
            query = query.filter_by(id_insumo=id_insumo)
        if id_atividade_agricola:
            query = query.filter_by(id_atividade_agricola=id_atividade_agricola)

        movimentacoes = query.order_by(MovimentacaoEstoque.data_movimentacao.desc()).all()
        return [MovimentacaoService.serializar(mov) for mov in movimentacoes]
