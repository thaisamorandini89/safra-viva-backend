"""Consultas determinísticas usadas pelo agente SafraIA.

Todos os números das respostas saem daqui; o LLM apenas escolhe a consulta e
redige o texto. Toda consulta é filtrada pela empresa do usuário autenticado.
"""
import datetime
from collections import defaultdict
from decimal import Decimal

from models.atividade_agricola import AtividadeAgricola
from models.funcionario import Funcionario
from models.insumo import Insumo
from models.lancamento_financeiro import LancamentoFinanceiro
from models.lote_insumo import LoteInsumo
from models.produto import Produto
from models.propriedade import Propriedade
from models.safra import Safra
from models.talhao import Talhao

LIMITE_LINHAS = 15


def _num(valor):
    if valor is None:
        return 0.0
    return float(valor) if isinstance(valor, Decimal) else float(valor)


def _moeda(valor):
    texto = f"{valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"R$ {texto}"


def _area(valor):
    return f"{valor:,.2f} ha".replace(',', 'X').replace('.', ',').replace('X', '.')


def _data(valor):
    if not valor:
        return None
    if isinstance(valor, datetime.date):
        return valor
    return datetime.date.fromisoformat(str(valor)[:10])


def _ids_propriedades(id_empresa):
    return [p.id_propriedade for p in
            Propriedade.query.filter_by(id_empresa=id_empresa).all()]


def _resultado(dados, destaques=None, tabela=None, alertas=None):
    return {
        'dados': dados,
        'destaques': destaques or [],
        'tabela': tabela,
        'alertas': alertas or [],
    }


def area_disponivel(id_empresa, cultura=None):
    props = _ids_propriedades(id_empresa)
    talhoes = Talhao.query.filter(Talhao.id_propriedade.in_(props), Talhao.status.is_(True)).all() if props else []
    livres = [t for t in talhoes if (t.status_inicial or 'Livre').lower() == 'livre']
    area_livre = sum(_num(t.area_utilizavel or t.area_total) for t in livres)
    area_total = sum(_num(t.area_utilizavel or t.area_total) for t in talhoes)
    linhas = [[t.codigo_talhao, t.nome_talhao, t.status_inicial or 'Livre', _area(_num(t.area_utilizavel or t.area_total))]
              for t in talhoes[:LIMITE_LINHAS]]
    dados = {
        'talhoes_total': len(talhoes),
        'talhoes_livres': len(livres),
        'area_livre_ha': round(area_livre, 2),
        'area_total_ha': round(area_total, 2),
    }
    if cultura:
        dados['simulacao'] = f"Plantando {cultura} em todos os talhões livres, a área cultivada com {cultura} seria {round(area_livre, 2)} ha."
    return _resultado(
        dados,
        destaques=[
            {'rotulo': 'Área livre', 'valor': _area(area_livre), 'tom': 'positivo' if area_livre else 'neutro'},
            {'rotulo': 'Talhões livres', 'valor': f"{len(livres)} de {len(talhoes)}"},
        ],
        tabela={'titulo': 'Talhões', 'colunas': ['Código', 'Talhão', 'Situação', 'Área útil'], 'linhas': linhas} if linhas else None,
    )


def safras(id_empresa):
    props = _ids_propriedades(id_empresa)
    registros = Safra.query.filter(Safra.id_propriedade.in_(props)).order_by(Safra.data_inicio.desc()).all() if props else []
    por_cultura = defaultdict(float)
    for s in registros:
        por_cultura[s.cultura] += _num(s.area_plantada)
    linhas = [[s.nome, s.cultura, str(s.data_inicio), str(s.data_fim or '-'), _area(_num(s.area_plantada))]
              for s in registros[:LIMITE_LINHAS]]
    return _resultado(
        {
            'quantidade_safras': len(registros),
            'area_plantada_por_cultura_ha': {k: round(v, 2) for k, v in por_cultura.items()},
            'observacao': 'O sistema ainda não registra produção colhida; produtividade (sc/ha) não pode ser calculada.',
        },
        destaques=[{'rotulo': c, 'valor': _area(a)} for c, a in list(por_cultura.items())[:4]],
        tabela={'titulo': 'Safras', 'colunas': ['Safra', 'Cultura', 'Início', 'Fim', 'Área plantada'], 'linhas': linhas} if linhas else None,
    )


def estoque(id_empresa, apenas_criticos=False):
    props = _ids_propriedades(id_empresa)
    query = Insumo.query.join(Produto, Insumo.id_produto == Produto.id_produto) \
        .filter(Insumo.id_propriedade.in_(props), Insumo.status.is_(True)) if props else None
    itens = []
    for insumo in (query.all() if query is not None else []):
        produto = Produto.query.get(insumo.id_produto)
        atual, minimo = _num(insumo.estoque_atual), _num(insumo.estoque_minimo)
        critico = minimo > 0 and atual <= minimo
        if apenas_criticos and not critico:
            continue
        itens.append({
            'produto': produto.nome_produto if produto else f"Insumo {insumo.id_insumo}",
            'unidade': produto.unidade_medida if produto else '',
            'estoque_atual': atual,
            'estoque_minimo': minimo,
            'critico': critico,
            'valor_estoque': round(atual * _num(insumo.valor_unitario), 2),
        })
    criticos = [i for i in itens if i['critico']]
    return _resultado(
        {'itens': itens[:LIMITE_LINHAS], 'total_itens': len(itens), 'itens_criticos': len(criticos)},
        destaques=[
            {'rotulo': 'Itens em estoque', 'valor': str(len(itens))},
            {'rotulo': 'Abaixo do mínimo', 'valor': str(len(criticos)), 'tom': 'critico' if criticos else 'positivo'},
        ],
        tabela={
            'titulo': 'Estoque',
            'colunas': ['Produto', 'Atual', 'Mínimo', 'Situação'],
            'linhas': [[i['produto'], f"{i['estoque_atual']:g} {i['unidade']}", f"{i['estoque_minimo']:g}",
                        'Crítico' if i['critico'] else 'OK'] for i in itens[:LIMITE_LINHAS]],
        } if itens else None,
        alertas=[{'nivel': 'critico', 'titulo': f"{i['produto']} atingiu o estoque mínimo"} for i in criticos[:5]],
    )


def lotes_a_vencer(id_empresa, dias=30):
    hoje = datetime.date.today()
    limite = hoje + datetime.timedelta(days=int(dias or 30))
    props = _ids_propriedades(id_empresa)
    if not props:
        return _resultado({'lotes': [], 'valor_em_risco': 0})
    lotes = LoteInsumo.query.join(Insumo, LoteInsumo.id_insumo == Insumo.id_insumo) \
        .filter(Insumo.id_propriedade.in_(props), LoteInsumo.data_validade.isnot(None),
                LoteInsumo.data_validade <= limite, LoteInsumo.quantidade > 0) \
        .order_by(LoteInsumo.data_validade).all()
    itens, valor_risco = [], 0.0
    for lote in lotes:
        insumo = Insumo.query.get(lote.id_insumo)
        produto = Produto.query.get(insumo.id_produto) if insumo else None
        valor = _num(lote.quantidade) * _num(insumo.valor_unitario if insumo else 0)
        valor_risco += valor
        dias_restantes = (lote.data_validade - hoje).days
        itens.append({
            'produto': produto.nome_produto if produto else '',
            'lote': lote.numero_lote,
            'validade': str(lote.data_validade),
            'dias_restantes': dias_restantes,
            'vencido': dias_restantes < 0,
            'quantidade': _num(lote.quantidade),
            'valor_estimado': round(valor, 2),
        })
    vencidos = [i for i in itens if i['vencido']]
    return _resultado(
        {'lotes': itens[:LIMITE_LINHAS], 'quantidade_lotes': len(itens), 'vencidos': len(vencidos),
         'valor_em_risco': round(valor_risco, 2), 'janela_dias': int(dias or 30)},
        destaques=[
            {'rotulo': 'Lotes a vencer/vencidos', 'valor': str(len(itens)), 'tom': 'atencao' if itens else 'positivo'},
            {'rotulo': 'Valor em risco', 'valor': _moeda(valor_risco), 'tom': 'critico' if valor_risco else 'neutro'},
        ],
        tabela={
            'titulo': 'Validade por lote',
            'colunas': ['Produto', 'Lote', 'Validade', 'Dias', 'Valor'],
            'linhas': [[i['produto'], i['lote'], i['validade'], i['dias_restantes'], _moeda(i['valor_estimado'])]
                       for i in itens[:LIMITE_LINHAS]],
        } if itens else None,
        alertas=[{'nivel': 'critico' if i['vencido'] else 'alerta',
                  'titulo': f"{i['produto']} (lote {i['lote']}) {'vencido' if i['vencido'] else 'vence em ' + str(i['dias_restantes']) + ' dias'}"}
                 for i in itens[:5]],
    )


def atividades(id_empresa):
    hoje = datetime.date.today()
    props = _ids_propriedades(id_empresa)
    registros = AtividadeAgricola.query.filter(AtividadeAgricola.id_propriedade.in_(props)).all() if props else []
    por_status = defaultdict(int)
    atrasadas = []
    for a in registros:
        por_status[a.status] += 1
        if a.status != 'Concluída' and a.data_fim and _data(a.data_fim) < hoje:
            atrasadas.append(a)
    total = len(registros)
    concluidas = por_status.get('Concluída', 0)
    percentual = round(concluidas / total * 100, 1) if total else 0
    return _resultado(
        {'total': total, 'por_status': dict(por_status), 'percentual_concluido': percentual, 'atrasadas': len(atrasadas)},
        destaques=[
            {'rotulo': 'Concluídas', 'valor': f"{percentual}%", 'tom': 'positivo' if percentual >= 80 else 'atencao'},
            {'rotulo': 'Atrasadas', 'valor': str(len(atrasadas)), 'tom': 'critico' if atrasadas else 'positivo'},
        ],
        tabela={'titulo': 'Atividades por status', 'colunas': ['Status', 'Quantidade'],
                'linhas': [[k, v] for k, v in por_status.items()]} if por_status else None,
        alertas=[{'nivel': 'alerta', 'titulo': f"{len(atrasadas)} atividade(s) atrasada(s)"}] if atrasadas else [],
    )


def funcionarios(id_empresa):
    props = _ids_propriedades(id_empresa)
    registros = AtividadeAgricola.query.filter(AtividadeAgricola.id_propriedade.in_(props),
                                               AtividadeAgricola.id_funcionario.isnot(None)).all() if props else []
    contagem = defaultdict(lambda: {'total': 0, 'concluidas': 0})
    for a in registros:
        contagem[a.id_funcionario]['total'] += 1
        if a.status == 'Concluída':
            contagem[a.id_funcionario]['concluidas'] += 1
    ranking = []
    for id_func, c in contagem.items():
        f = Funcionario.query.get(id_func)
        ranking.append({'funcionario': f.nome_completo if f else f"#{id_func}", 'cargo': f.cargo if f else '', **c})
    ranking.sort(key=lambda r: (r['concluidas'], r['total']), reverse=True)
    return _resultado(
        {'ranking': ranking[:LIMITE_LINHAS]},
        destaques=[{'rotulo': 'Mais atividades', 'valor': ranking[0]['funcionario'], 'tom': 'positivo'}] if ranking else [],
        tabela={'titulo': 'Atividades por funcionário', 'colunas': ['Funcionário', 'Cargo', 'Atividades', 'Concluídas'],
                'linhas': [[r['funcionario'], r['cargo'], r['total'], r['concluidas']] for r in ranking[:LIMITE_LINHAS]]}
        if ranking else None,
    )


def _lancamentos(id_empresa, inicio=None, fim=None):
    query = LancamentoFinanceiro.query.filter(LancamentoFinanceiro.id_empresa == id_empresa)
    if inicio:
        query = query.filter(LancamentoFinanceiro.data_lancamento >= _data(inicio))
    if fim:
        query = query.filter(LancamentoFinanceiro.data_lancamento <= _data(fim))
    return query.all()


def custos(id_empresa, data_inicio=None, data_fim=None, categoria=None):
    despesas = [l for l in _lancamentos(id_empresa, data_inicio, data_fim) if l.tipo == 'DESPESA']
    if categoria:
        despesas = [l for l in despesas if categoria.lower() in (l.categoria or '').lower()
                    or categoria.lower() in (l.descricao or '').lower()]
    por_categoria = defaultdict(float)
    for l in despesas:
        por_categoria[l.categoria] += _num(l.valor)
    total = sum(por_categoria.values())
    ordenado = sorted(por_categoria.items(), key=lambda kv: kv[1], reverse=True)
    return _resultado(
        {'total_despesas': round(total, 2), 'por_categoria': {k: round(v, 2) for k, v in ordenado},
         'periodo': {'inicio': data_inicio, 'fim': data_fim}, 'filtro_categoria': categoria},
        destaques=[{'rotulo': 'Total de despesas', 'valor': _moeda(total), 'tom': 'atencao'}]
        + ([{'rotulo': 'Maior categoria', 'valor': ordenado[0][0]}] if ordenado else []),
        tabela={'titulo': 'Despesas por categoria', 'colunas': ['Categoria', 'Valor'],
                'linhas': [[k, _moeda(v)] for k, v in ordenado[:LIMITE_LINHAS]]} if ordenado else None,
    )


def lucro_safra(id_empresa):
    linhas_por_safra = defaultdict(lambda: {'receitas': 0.0, 'despesas': 0.0})
    for l in _lancamentos(id_empresa):
        chave = l.id_safra or 0
        linhas_por_safra[chave]['receitas' if l.tipo == 'RECEITA' else 'despesas'] += _num(l.valor)
    resultado = []
    for id_safra, v in linhas_por_safra.items():
        s = Safra.query.get(id_safra) if id_safra else None
        resultado.append({'safra': s.nome if s else 'Sem safra', 'receitas': round(v['receitas'], 2),
                          'despesas': round(v['despesas'], 2), 'lucro': round(v['receitas'] - v['despesas'], 2)})
    resultado.sort(key=lambda r: r['lucro'], reverse=True)
    total = sum(r['lucro'] for r in resultado)
    return _resultado(
        {'por_safra': resultado[:LIMITE_LINHAS], 'lucro_total': round(total, 2)},
        destaques=[{'rotulo': 'Resultado total', 'valor': _moeda(total), 'tom': 'positivo' if total >= 0 else 'critico'}],
        tabela={'titulo': 'Resultado por safra', 'colunas': ['Safra', 'Receitas', 'Despesas', 'Lucro'],
                'linhas': [[r['safra'], _moeda(r['receitas']), _moeda(r['despesas']), _moeda(r['lucro'])]
                           for r in resultado[:LIMITE_LINHAS]]} if resultado else None,
    )


# Declaração das consultas para o LLM (function calling). "financeiro" restringe por perfil.
TOOLS = {
    'area_disponivel': {
        'funcao': area_disponivel, 'financeiro': False,
        'descricao': 'Talhões livres e ocupados, área disponível para plantio e simulação de plantar uma cultura em todos os talhões livres.',
        'parametros': {'type': 'object', 'properties': {
            'cultura': {'type': 'string', 'description': 'Cultura a simular nos talhões livres (opcional).'}}},
    },
    'safras': {
        'funcao': safras, 'financeiro': False,
        'descricao': 'Safras cadastradas, culturas e área plantada por cultura (base para análises de produtividade e planejamento).',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'estoque': {
        'funcao': estoque, 'financeiro': False,
        'descricao': 'Situação do estoque de insumos, incluindo itens abaixo do estoque mínimo.',
        'parametros': {'type': 'object', 'properties': {
            'apenas_criticos': {'type': 'boolean', 'description': 'Somente itens no mínimo ou abaixo.'}}},
    },
    'lotes_a_vencer': {
        'funcao': lotes_a_vencer, 'financeiro': False,
        'descricao': 'Lotes de insumos e fertilizantes vencidos ou a vencer, com valor estimado em risco.',
        'parametros': {'type': 'object', 'properties': {
            'dias': {'type': 'integer', 'description': 'Janela em dias a partir de hoje (padrão 30).'}}},
    },
    'atividades': {
        'funcao': atividades, 'financeiro': False,
        'descricao': 'Atividades agrícolas por status, percentual concluído e atividades atrasadas.',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'funcionarios': {
        'funcao': funcionarios, 'financeiro': False,
        'descricao': 'Ranking de funcionários por atividades executadas e concluídas.',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'custos': {
        'funcao': custos, 'financeiro': True,
        'descricao': 'Despesas por categoria em um período (ex.: gastos com fertilizantes no mês).',
        'parametros': {'type': 'object', 'properties': {
            'data_inicio': {'type': 'string', 'description': 'Data inicial AAAA-MM-DD.'},
            'data_fim': {'type': 'string', 'description': 'Data final AAAA-MM-DD.'},
            'categoria': {'type': 'string', 'description': 'Filtro por categoria ou descrição (ex.: fertilizante).'}}},
    },
    'lucro_safra': {
        'funcao': lucro_safra, 'financeiro': True,
        'descricao': 'Receitas, despesas e lucro por safra.',
        'parametros': {'type': 'object', 'properties': {}},
    },
}


def tools_permitidas(perfil_financeiro):
    return {nome: t for nome, t in TOOLS.items() if perfil_financeiro or not t['financeiro']}


def executar_tool(nome, argumentos, id_empresa, perfil_financeiro):
    tool = TOOLS.get(nome)
    if tool is None:
        return {'erro': f'Consulta desconhecida: {nome}'}
    if tool['financeiro'] and not perfil_financeiro:
        return {'erro': 'Seu perfil não tem acesso a dados financeiros.'}
    permitidos = set(tool['parametros']['properties'])
    kwargs = {k: v for k, v in (argumentos or {}).items() if k in permitidos and v not in (None, '')}
    try:
        return tool['funcao'](id_empresa, **kwargs)
    except (ValueError, TypeError) as exc:
        return {'erro': f'Parâmetros inválidos: {exc}'}
