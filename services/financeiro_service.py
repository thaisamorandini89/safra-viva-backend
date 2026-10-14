from decimal import Decimal

from models.lancamento_financeiro import LancamentoFinanceiro
from models.rateio_lancamento import RateioLancamento
from models.talhao import Talhao
from models.safra import Safra


def _aplicar_filtros(query, filtros):
    if filtros.get("data_inicio"):
        query = query.filter(
            LancamentoFinanceiro.data_lancamento >= filtros["data_inicio"]
        )
    if filtros.get("data_fim"):
        query = query.filter(
            LancamentoFinanceiro.data_lancamento <= filtros["data_fim"]
        )
    if filtros.get("id_propriedade"):
        query = query.filter(
            LancamentoFinanceiro.id_propriedade == filtros["id_propriedade"]
        )
    if filtros.get("id_safra"):
        query = query.filter(LancamentoFinanceiro.id_safra == filtros["id_safra"])
    return query


def _f(valor):
    return float(valor or 0)


class FinanceiroService:
    @staticmethod
    def saldo(filtros=None):
        filtros = filtros or {}
        query = _aplicar_filtros(LancamentoFinanceiro.query, filtros)
        lancamentos = query.all()
        receita = sum((l.valor for l in lancamentos if l.tipo == "RECEITA"), Decimal(0))
        despesa = sum((l.valor for l in lancamentos if l.tipo == "DESPESA"), Decimal(0))
        return {
            "receita_total": _f(receita),
            "despesa_total": _f(despesa),
            "saldo": _f(receita - despesa),
        }

    @staticmethod
    def fluxo_caixa(data_inicio=None, data_fim=None):
        query = LancamentoFinanceiro.query
        if data_inicio:
            query = query.filter(LancamentoFinanceiro.data_lancamento >= data_inicio)
        if data_fim:
            query = query.filter(LancamentoFinanceiro.data_lancamento <= data_fim)
        lancamentos = query.order_by(
            LancamentoFinanceiro.data_lancamento.asc()
        ).all()

        itens = []
        saldo = Decimal(0)
        for l in lancamentos:
            entrada = l.valor if l.tipo == "RECEITA" else Decimal(0)
            saida = l.valor if l.tipo == "DESPESA" else Decimal(0)
            saldo += entrada - saida
            itens.append({
                "data": l.data_lancamento.isoformat() if l.data_lancamento else None,
                "descricao": l.descricao or l.categoria,
                "entrada": _f(entrada),
                "saida": _f(saida),
                "saldo": _f(saldo),
            })
        return itens

    @staticmethod
    def indicadores(agrupar_por):
        if agrupar_por not in ("safra", "talhao", "cultura"):
            raise ValueError(
                "agrupar_por deve ser um de: safra, talhao, cultura."
            )

        grupos = {}  # chave -> {receita, despesa, area}

        def garante(chave, area):
            if chave not in grupos:
                grupos[chave] = {"receita": Decimal(0), "despesa": Decimal(0), "area": area}
            return grupos[chave]

        lancamentos = LancamentoFinanceiro.query.all()

        if agrupar_por == "talhao":
            talhoes = {t.id_talhao: t for t in Talhao.query.all()}
            for l in lancamentos:
                partes = []
                if l.rateios:
                    for r in l.rateios:
                        partes.append((r.id_talhao, l.valor * Decimal(r.percentual) / Decimal(100)))
                elif l.id_talhao:
                    partes.append((l.id_talhao, l.valor))
                for id_talhao, valor in partes:
                    t = talhoes.get(id_talhao)
                    chave = t.nome_talhao if t else f"Talhão {id_talhao}"
                    area = float(t.area_total) if t and t.area_total else None
                    g = garante(chave, area)
                    if l.tipo == "RECEITA":
                        g["receita"] += valor
                    else:
                        g["despesa"] += valor
        else:
            safras = {s.id_safra: s for s in Safra.query.all()}
            # área total por cultura (soma das áreas das safras daquela cultura)
            area_cultura = {}
            for s in safras.values():
                if s.cultura:
                    area_cultura[s.cultura] = area_cultura.get(s.cultura, 0) + float(
                        s.area_plantada or 0
                    )
            for l in lancamentos:
                if not l.id_safra:
                    continue
                s = safras.get(l.id_safra)
                if not s:
                    continue
                if agrupar_por == "safra":
                    chave = s.nome
                    area = float(s.area_plantada) if s.area_plantada else None
                else:  # cultura
                    chave = s.cultura
                    area = area_cultura.get(s.cultura) or None
                g = garante(chave, area)
                if l.tipo == "RECEITA":
                    g["receita"] += l.valor
                else:
                    g["despesa"] += l.valor

        resultado = []
        for chave, g in grupos.items():
            receita = g["receita"]
            despesa = g["despesa"]
            lucro = receita - despesa
            area = g["area"] if g["area"] and g["area"] > 0 else None
            resultado.append({
                "grupo": chave,
                "receita_total": _f(receita),
                "despesa_total": _f(despesa),
                "lucro_liquido": _f(lucro),
                "margem": float(lucro / receita * 100) if receita > 0 else 0.0,
                "roi": float(lucro / despesa * 100) if despesa > 0 else 0.0,
                "area": area,
                "custo_por_hectare": _f(despesa) / area if area else None,
                "receita_por_hectare": _f(receita) / area if area else None,
                "lucro_por_hectare": _f(lucro) / area if area else None,
            })

        resultado.sort(key=lambda x: x["lucro_liquido"], reverse=True)
        return resultado
