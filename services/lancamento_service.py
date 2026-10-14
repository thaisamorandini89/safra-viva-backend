from decimal import Decimal

from models import db
from models.lancamento_financeiro import LancamentoFinanceiro
from models.rateio_lancamento import RateioLancamento
from models.empresa_agricola import EmpresaAgricola
from models.propriedade import Propriedade
from models.talhao import Talhao
from models.safra import Safra
from models.centro_custo import CentroCusto


def serializar_lancamento(l):
    prop = Propriedade.query.get(l.id_propriedade) if l.id_propriedade else None
    talhao = Talhao.query.get(l.id_talhao) if l.id_talhao else None
    safra = Safra.query.get(l.id_safra) if l.id_safra else None

    rateio = []
    for r in (l.rateios or []):
        t = Talhao.query.get(r.id_talhao)
        rateio.append({
            "id_rateio": r.id_rateio,
            "id_talhao": r.id_talhao,
            "nome_talhao": t.nome_talhao if t else None,
            "percentual": float(r.percentual),
        })

    return {
        "id_lancamento": l.id_lancamento,
        "tipo": l.tipo,
        "categoria": l.categoria,
        "descricao": l.descricao,
        "valor": float(l.valor),
        "data_lancamento": l.data_lancamento.isoformat() if l.data_lancamento else None,
        "forma_pagamento": l.forma_pagamento,
        "status": l.status,
        "conciliado": l.conciliado,
        "observacao": l.observacao,
        "id_empresa": l.id_empresa,
        "id_propriedade": l.id_propriedade,
        "id_talhao": l.id_talhao,
        "id_safra": l.id_safra,
        "id_centro_custo": l.id_centro_custo,
        "nome_propriedade": prop.nome_propriedade if prop else None,
        "nome_talhao": talhao.nome_talhao if talhao else None,
        "nome_safra": safra.nome if safra else None,
        "cultura": safra.cultura if safra else None,
        "rateio": rateio,
    }


def _validar_vinculos(dados):
    if dados.id_empresa and not EmpresaAgricola.query.get(dados.id_empresa):
        raise ValueError("Empresa informada não foi encontrada.")
    if dados.id_propriedade and not Propriedade.query.get(dados.id_propriedade):
        raise ValueError("Propriedade informada não foi encontrada.")
    if dados.id_talhao and not Talhao.query.get(dados.id_talhao):
        raise ValueError("Talhão informado não foi encontrado.")
    if dados.id_safra and not Safra.query.get(dados.id_safra):
        raise ValueError("Safra informada não foi encontrada.")
    if dados.id_centro_custo and not CentroCusto.query.get(dados.id_centro_custo):
        raise ValueError("Centro de custo informado não foi encontrado.")


def _validar_rateio(dados):
    """Valida existência dos talhões e soma dos percentuais (RN005)."""
    if not dados.rateio:
        return
    soma = Decimal(0)
    for item in dados.rateio:
        if not Talhao.query.get(item.id_talhao):
            raise ValueError(
                f"Talhão {item.id_talhao} do rateio não foi encontrado."
            )
        soma += Decimal(item.percentual)
    if abs(soma - Decimal(100)) > Decimal("0.01"):
        raise ValueError(
            f"A soma dos percentuais do rateio deve ser 100% (atual: {soma}%)."
        )


class LancamentoService:
    @staticmethod
    def criar(dados):
        """Cria um lançamento e suas parcelas de rateio na mesma transação."""
        _validar_vinculos(dados)
        _validar_rateio(dados)

        lancamento = LancamentoFinanceiro(
            tipo=dados.tipo,
            categoria=dados.categoria,
            descricao=dados.descricao,
            valor=Decimal(dados.valor),
            data_lancamento=dados.data_lancamento,
            forma_pagamento=dados.forma_pagamento,
            status=dados.status or "PENDENTE",
            observacao=dados.observacao,
            id_empresa=dados.id_empresa,
            id_propriedade=dados.id_propriedade,
            id_talhao=dados.id_talhao,
            id_safra=dados.id_safra,
            id_centro_custo=dados.id_centro_custo,
        )
        if dados.rateio:
            lancamento.rateios = [
                RateioLancamento(
                    id_talhao=item.id_talhao,
                    percentual=Decimal(item.percentual),
                )
                for item in dados.rateio
            ]

        db.session.add(lancamento)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao criar o lançamento: {str(e)}")
        return lancamento

    @staticmethod
    def atualizar(id_lancamento, dados):
        """Atualiza um lançamento existente (404 se inexistente)."""
        lancamento = LancamentoFinanceiro.query.get(id_lancamento)
        if not lancamento:
            raise LookupError("Lançamento não encontrado.")

        _validar_vinculos(dados)
        _validar_rateio(dados)

        lancamento.tipo = dados.tipo
        lancamento.categoria = dados.categoria
        lancamento.descricao = dados.descricao
        lancamento.valor = Decimal(dados.valor)
        lancamento.data_lancamento = dados.data_lancamento
        lancamento.forma_pagamento = dados.forma_pagamento
        lancamento.status = dados.status or lancamento.status
        lancamento.observacao = dados.observacao
        lancamento.id_empresa = dados.id_empresa
        lancamento.id_propriedade = dados.id_propriedade
        lancamento.id_talhao = dados.id_talhao
        lancamento.id_safra = dados.id_safra
        lancamento.id_centro_custo = dados.id_centro_custo

        # Substitui o rateio
        lancamento.rateios = [
            RateioLancamento(
                id_talhao=item.id_talhao,
                percentual=Decimal(item.percentual),
            )
            for item in (dados.rateio or [])
        ]

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao atualizar o lançamento: {str(e)}")
        return lancamento

    @staticmethod
    def excluir(id_lancamento):
        """Exclui um lançamento, bloqueando lançamentos conciliados (RN003)."""
        lancamento = LancamentoFinanceiro.query.get(id_lancamento)
        if not lancamento:
            raise LookupError("Lançamento não encontrado.")
        if lancamento.conciliado:
            raise ValueError("Lançamentos conciliados não podem ser excluídos.")

        db.session.delete(lancamento)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Erro ao excluir o lançamento: {str(e)}")

    @staticmethod
    def listar(filtros=None):
        """Lista lançamentos ordenados por data desc, com filtros opcionais."""
        filtros = filtros or {}
        query = LancamentoFinanceiro.query

        if filtros.get("data_inicio"):
            query = query.filter(
                LancamentoFinanceiro.data_lancamento >= filtros["data_inicio"]
            )
        if filtros.get("data_fim"):
            query = query.filter(
                LancamentoFinanceiro.data_lancamento <= filtros["data_fim"]
            )
        if filtros.get("tipo"):
            query = query.filter(LancamentoFinanceiro.tipo == filtros["tipo"])
        if filtros.get("id_safra"):
            query = query.filter(LancamentoFinanceiro.id_safra == filtros["id_safra"])
        if filtros.get("id_propriedade"):
            query = query.filter(
                LancamentoFinanceiro.id_propriedade == filtros["id_propriedade"]
            )
        if filtros.get("id_talhao"):
            id_talhao = filtros["id_talhao"]
            sub = (
                db.session.query(RateioLancamento.id_lancamento)
                .filter(RateioLancamento.id_talhao == id_talhao)
            )
            query = query.filter(
                db.or_(
                    LancamentoFinanceiro.id_talhao == id_talhao,
                    LancamentoFinanceiro.id_lancamento.in_(sub),
                )
            )

        lancamentos = query.order_by(
            LancamentoFinanceiro.data_lancamento.desc()
        ).all()
        return [serializar_lancamento(l) for l in lancamentos]
