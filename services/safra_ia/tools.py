"""Consultas determinísticas usadas pelo agente SafraIA.

Todos os números das respostas saem daqui; o LLM apenas escolhe a consulta e
redige o texto. Toda consulta é filtrada pela empresa do usuário autenticado.
"""
import datetime
from collections import defaultdict
from decimal import Decimal
from inspect import signature

from sqlalchemy import or_

from models import db
from models.atividade_agricola import AtividadeAgricola
from models.atividade_insumo import AtividadeInsumo
from models.atividade_maquina import AtividadeMaquina
from models.centro_custo import CentroCusto
from models.fornecedor import Fornecedor
from models.funcionario import Funcionario
from models.funcionario_propriedade import FuncionarioPropriedade
from models.insumo import Insumo
from models.lancamento_financeiro import LancamentoFinanceiro
from models.lote_insumo import LoteInsumo
from models.maquina import Maquina
from models.movimentacao_estoque import MovimentacaoEstoque
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


def resumo_propriedades(id_empresa):
    propriedades = Propriedade.query.filter_by(id_empresa=id_empresa, status=True) \
        .order_by(Propriedade.nome_propriedade).all()
    linhas = []
    totais = {
        'area_total_ha': 0.0,
        'area_agricultavel_ha': 0.0,
        'area_preservacao_ha': 0.0,
        'area_pastagem_ha': 0.0,
        'talhoes_ativos': 0,
    }
    for propriedade in propriedades:
        areas = {
            'area_total_ha': _num(propriedade.area_total),
            'area_agricultavel_ha': _num(propriedade.area_agricultavel),
            'area_preservacao_ha': _num(propriedade.area_preservacao),
            'area_pastagem_ha': _num(propriedade.area_pastagem),
        }
        talhoes_ativos = Talhao.query.filter_by(
            id_propriedade=propriedade.id_propriedade, status=True
        ).count()
        for campo, valor in areas.items():
            totais[campo] += valor
        totais['talhoes_ativos'] += talhoes_ativos
        linhas.append([
            propriedade.nome_propriedade,
            _area(areas['area_total_ha']),
            _area(areas['area_agricultavel_ha']),
            _area(areas['area_preservacao_ha']),
            _area(areas['area_pastagem_ha']),
            talhoes_ativos,
        ])
    for campo in ('area_total_ha', 'area_agricultavel_ha', 'area_preservacao_ha', 'area_pastagem_ha'):
        totais[campo] = round(totais[campo], 2)
    dados = {'propriedades_ativas': len(propriedades), **totais}
    return _resultado(
        dados,
        destaques=[
            {'rotulo': 'Propriedades', 'valor': str(len(propriedades))},
            {'rotulo': 'Área total', 'valor': _area(totais['area_total_ha'])},
            {'rotulo': 'Talhões ativos', 'valor': str(totais['talhoes_ativos'])},
        ],
        tabela={
            'titulo': 'Propriedades',
            'colunas': ['Propriedade', 'Área total', 'Agricultável', 'Preservação', 'Pastagem', 'Talhões ativos'],
            'linhas': linhas,
        } if linhas else None,
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


def equipe(id_empresa):
    registros = db.session.query(
        Propriedade.nome_propriedade,
        Funcionario.cargo,
        Funcionario.id_funcionario,
    ).join(
        FuncionarioPropriedade, FuncionarioPropriedade.id_propriedade == Propriedade.id_propriedade
    ).join(
        Funcionario, Funcionario.id_funcionario == FuncionarioPropriedade.id_funcionario
    ).filter(
        Propriedade.id_empresa == id_empresa,
        Propriedade.status.is_(True),
        Funcionario.status.is_(True),
        Funcionario.data_desligamento.is_(None),
    ).order_by(Propriedade.nome_propriedade, Funcionario.cargo).all()

    por_grupo = defaultdict(set)
    funcionarios_unicos = set()
    for nome_propriedade, cargo, id_funcionario in registros:
        por_grupo[(nome_propriedade, cargo)].add(id_funcionario)
        funcionarios_unicos.add(id_funcionario)
    linhas = [
        [propriedade, cargo, len(ids)]
        for (propriedade, cargo), ids in sorted(por_grupo.items())
    ]
    return _resultado(
        {'total_funcionarios': len(funcionarios_unicos), 'grupos': len(linhas)},
        destaques=[{'rotulo': 'Funcionários ativos', 'valor': str(len(funcionarios_unicos))}],
        tabela={
            'titulo': 'Equipe por propriedade e cargo',
            'colunas': ['Propriedade', 'Cargo', 'Funcionários ativos'],
            'linhas': linhas[:LIMITE_LINHAS],
        } if linhas else None,
    )


def maquinas(id_empresa, ver_valores=False):
    props = _ids_propriedades(id_empresa)
    registros = db.session.query(
        Maquina.nome,
        AtividadeMaquina.nome,
        AtividadeMaquina.id_atividade_agricola,
        AtividadeMaquina.horas,
        AtividadeMaquina.custo,
    ).join(
        AtividadeMaquina, AtividadeMaquina.id_maquina == Maquina.id_maquina
    ).join(
        AtividadeAgricola, AtividadeAgricola.id_atividade_agricola == AtividadeMaquina.id_atividade_agricola
    ).filter(
        AtividadeAgricola.id_propriedade.in_(props)
    ).all() if props else []

    agregados = {}
    for nome, nome_snapshot, id_atividade, horas, custo in registros:
        nome_maquina = nome or nome_snapshot or 'Máquina sem nome'
        item = agregados.setdefault(nome_maquina, {'horas': 0.0, 'atividades': set(), 'custo': 0.0})
        item['horas'] += _num(horas)
        item['atividades'].add(id_atividade)
        item['custo'] += _num(custo)
    ordenados = sorted(agregados.items(), key=lambda par: (par[1]['horas'], len(par[1]['atividades'])), reverse=True)
    linhas, itens = [], []
    for nome, item in ordenados[:LIMITE_LINHAS]:
        registro = {
            'maquina': nome,
            'horas': round(item['horas'], 2),
            'atividades': len(item['atividades']),
        }
        linha = [nome, f"{item['horas']:g}", len(item['atividades'])]
        if ver_valores:
            registro['custo_total'] = round(item['custo'], 2)
            linha.append(_moeda(item['custo']))
        itens.append(registro)
        linhas.append(linha)
    destaque = []
    if ordenados:
        nome, item = ordenados[0]
        destaque.append({'rotulo': 'Máquina mais usada', 'valor': nome})
        destaque.append({'rotulo': 'Horas de uso', 'valor': f"{item['horas']:g}"})
    colunas = ['Máquina', 'Horas', 'Atividades']
    if ver_valores:
        colunas.append('Custo')
    return _resultado(
        {'maquinas': itens, 'total_maquinas': len(agregados)},
        destaques=destaque,
        tabela={'titulo': 'Uso de máquinas', 'colunas': colunas, 'linhas': linhas} if linhas else None,
    )


def consumo_insumos(id_empresa, safra=None, talhao=None, ver_valores=False):
    props = _ids_propriedades(id_empresa)
    query = db.session.query(
        Produto.nome_produto,
        Produto.unidade_medida,
        AtividadeInsumo.nome,
        AtividadeInsumo.unidade,
        AtividadeInsumo.quantidade,
        AtividadeInsumo.custo,
    ).join(
        Insumo, Insumo.id_insumo == AtividadeInsumo.id_insumo
    ).join(
        Produto, Produto.id_produto == Insumo.id_produto
    ).join(
        AtividadeAgricola,
        AtividadeAgricola.id_atividade_agricola == AtividadeInsumo.id_atividade_agricola,
    ).join(
        Talhao, Talhao.id_talhao == AtividadeAgricola.id_talhao
    ).filter(
        Talhao.id_propriedade.in_(props)
    ) if props else None
    if query is None:
        registros = []
    else:
        if safra:
            query = query.filter(AtividadeAgricola.safra.ilike(f'%{safra}%'))
        if talhao:
            filtro_talhao = f'%{talhao}%'
            query = query.filter(
                or_(Talhao.nome_talhao.ilike(filtro_talhao), Talhao.codigo_talhao.ilike(filtro_talhao))
            )
        registros = query.all()

    agregados = {}
    for produto, unidade_produto, nome_snapshot, unidade_snapshot, quantidade, custo in registros:
        nome = produto or nome_snapshot or 'Insumo sem nome'
        unidade = unidade_snapshot or unidade_produto or ''
        item = agregados.setdefault((nome, unidade), {'quantidade': 0.0, 'custo': 0.0})
        item['quantidade'] += _num(quantidade)
        item['custo'] += _num(custo)
    itens, linhas = [], []
    for (nome, unidade), item in sorted(agregados.items()):
        registro = {
            'produto': nome,
            'quantidade': round(item['quantidade'], 3),
            'unidade': unidade,
        }
        linha = [nome, f"{item['quantidade']:g}", unidade]
        if ver_valores:
            registro['custo_total'] = round(item['custo'], 2)
            linha.append(_moeda(item['custo']))
        itens.append(registro)
        linhas.append(linha)
    colunas = ['Produto', 'Quantidade', 'Unidade']
    if ver_valores:
        colunas.append('Custo')
    return _resultado(
        {'itens': itens[:LIMITE_LINHAS], 'total_produtos': len(itens),
         'filtros': {'safra': safra, 'talhao': talhao}},
        destaques=[{'rotulo': 'Produtos aplicados', 'valor': str(len(itens))}],
        tabela={
            'titulo': 'Consumo de insumos',
            'colunas': colunas,
            'linhas': linhas[:LIMITE_LINHAS],
        } if linhas else None,
    )


def movimentacoes_estoque(id_empresa, dias=30, tipo=None, produto=None, ver_valores=False):
    dias = int(dias or 30)
    if dias < 1:
        raise ValueError('O período deve ser de pelo menos 1 dia.')
    tipo = (tipo or '').strip().upper()
    if tipo:
        tipo = {'SAÍDA': 'SAIDA', 'SAIDA': 'SAIDA', 'ENTRADA': 'ENTRADA'}.get(tipo)
        if tipo is None:
            raise ValueError('O tipo deve ser ENTRADA ou SAIDA.')
    inicio = datetime.datetime.now() - datetime.timedelta(days=dias)
    props = _ids_propriedades(id_empresa)
    query = db.session.query(
        Produto.nome_produto,
        Produto.unidade_medida,
        MovimentacaoEstoque.tipo_movimentacao,
        MovimentacaoEstoque.quantidade,
        MovimentacaoEstoque.valor_unitario,
        MovimentacaoEstoque.data_movimentacao,
    ).join(
        Insumo, Insumo.id_insumo == MovimentacaoEstoque.id_insumo
    ).join(
        Produto, Produto.id_produto == Insumo.id_produto
    ).filter(
        Insumo.id_propriedade.in_(props),
        MovimentacaoEstoque.data_movimentacao >= inicio,
    ) if props else None
    if query is None:
        registros = []
    else:
        if tipo:
            query = query.filter(MovimentacaoEstoque.tipo_movimentacao == tipo)
        if produto:
            query = query.filter(Produto.nome_produto.ilike(f'%{produto}%'))
        registros = query.order_by(MovimentacaoEstoque.data_movimentacao.desc()).all()

    agregados = defaultdict(lambda: {'quantidade': 0.0, 'movimentacoes': 0, 'valor': 0.0, 'ultima': None})
    for nome, unidade, movimento, quantidade, valor_unitario, data in registros:
        item = agregados[(nome, unidade, movimento)]
        qtd = _num(quantidade)
        item['quantidade'] += qtd
        item['movimentacoes'] += 1
        item['valor'] += qtd * _num(valor_unitario)
        if item['ultima'] is None or data > item['ultima']:
            item['ultima'] = data
    itens, linhas = [], []
    for (nome, unidade, movimento), item in sorted(agregados.items()):
        registro = {
            'produto': nome,
            'tipo': movimento,
            'quantidade': round(item['quantidade'], 3),
            'unidade': unidade,
            'movimentacoes': item['movimentacoes'],
            'ultima_movimentacao': item['ultima'].date().isoformat() if item['ultima'] else None,
        }
        linha = [nome, movimento, f"{item['quantidade']:g} {unidade}", item['movimentacoes']]
        if ver_valores:
            registro['valor_total'] = round(item['valor'], 2)
            linha.append(_moeda(item['valor']))
        itens.append(registro)
        linhas.append(linha)
    colunas = ['Produto', 'Tipo', 'Quantidade', 'Movimentações']
    if ver_valores:
        colunas.append('Valor')
    return _resultado(
        {'itens': itens[:LIMITE_LINHAS], 'total_movimentacoes': sum(i['movimentacoes'] for i in itens),
         'periodo_dias': dias, 'data_inicio': inicio.date().isoformat()},
        destaques=[{'rotulo': 'Movimentações', 'valor': str(sum(i['movimentacoes'] for i in itens))}],
        tabela={
            'titulo': 'Movimentações de estoque',
            'colunas': colunas,
            'linhas': linhas[:LIMITE_LINHAS],
        } if linhas else None,
    )


def fornecedores(id_empresa, ver_valores=False):
    props = _ids_propriedades(id_empresa)
    registros = db.session.query(
        Fornecedor.id_fornecedor,
        Fornecedor.nome_fornecedor,
        MovimentacaoEstoque.quantidade,
        MovimentacaoEstoque.valor_unitario,
        MovimentacaoEstoque.data_movimentacao,
    ).join(
        MovimentacaoEstoque, MovimentacaoEstoque.id_fornecedor == Fornecedor.id_fornecedor
    ).join(
        Insumo, Insumo.id_insumo == MovimentacaoEstoque.id_insumo
    ).filter(
        Insumo.id_propriedade.in_(props),
        MovimentacaoEstoque.tipo_movimentacao == 'ENTRADA',
        MovimentacaoEstoque.id_fornecedor.isnot(None),
        Fornecedor.status.is_(True),
    ).all() if props else []
    agregados = {}
    for id_fornecedor, nome, quantidade, valor_unitario, data in registros:
        item = agregados.setdefault(id_fornecedor, {
            'fornecedor': nome,
            'entradas': 0,
            'ultima_entrada': None,
            'valor': 0.0,
        })
        item['entradas'] += 1
        item['valor'] += _num(quantidade) * _num(valor_unitario)
        if item['ultima_entrada'] is None or data > item['ultima_entrada']:
            item['ultima_entrada'] = data
    ordenados = sorted(
        agregados.values(),
        key=lambda item: (item['entradas'], item['ultima_entrada'] or datetime.datetime.min),
        reverse=True,
    )
    itens, linhas = [], []
    for item in ordenados[:LIMITE_LINHAS]:
        registro = {
            'fornecedor': item['fornecedor'],
            'entradas': item['entradas'],
            'ultima_entrada': item['ultima_entrada'].date().isoformat() if item['ultima_entrada'] else None,
        }
        linha = [item['fornecedor'], item['entradas'], registro['ultima_entrada']]
        if ver_valores:
            registro['valor_comprado'] = round(item['valor'], 2)
            linha.append(_moeda(item['valor']))
        itens.append(registro)
        linhas.append(linha)
    colunas = ['Fornecedor', 'Entradas', 'Última entrada']
    if ver_valores:
        colunas.append('Valor comprado')
    return _resultado(
        {'fornecedores': itens, 'total_fornecedores': len(agregados)},
        destaques=[
            {'rotulo': 'Fornecedores com entradas', 'valor': str(len(agregados))},
        ] + ([{'rotulo': 'Principal fornecedor', 'valor': itens[0]['fornecedor']}] if itens else []),
        tabela={
            'titulo': 'Fornecedores por entradas',
            'colunas': colunas,
            'linhas': linhas,
        } if linhas else None,
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


def fluxo_mensal(id_empresa, data_inicio=None, data_fim=None):
    hoje = datetime.date.today()
    fim = _data(data_fim) if data_fim else hoje
    if data_inicio:
        inicio = _data(data_inicio)
    else:
        ano, mes = hoje.year, hoje.month
        for _ in range(11):
            mes -= 1
            if mes == 0:
                ano -= 1
                mes = 12
        inicio = datetime.date(ano, mes, 1)
    if inicio > fim:
        raise ValueError('A data inicial deve ser anterior à data final.')
    lancamentos = _lancamentos(id_empresa, inicio, fim)
    por_mes = defaultdict(lambda: {'receitas': 0.0, 'despesas': 0.0})
    for lancamento in lancamentos:
        chave = _data(lancamento.data_lancamento).strftime('%Y-%m')
        campo = 'receitas' if lancamento.tipo == 'RECEITA' else 'despesas'
        por_mes[chave][campo] += _num(lancamento.valor)
    meses = []
    ano, mes = inicio.year, inicio.month
    while (ano, mes) <= (fim.year, fim.month):
        chave = f'{ano:04d}-{mes:02d}'
        valores = por_mes[chave]
        receita = round(valores['receitas'], 2)
        despesa = round(valores['despesas'], 2)
        saldo = round(receita - despesa, 2)
        meses.append({'mes': chave, 'receitas': receita, 'despesas': despesa, 'saldo': saldo})
        mes += 1
        if mes == 13:
            ano += 1
            mes = 1
    total_receitas = round(sum(m['receitas'] for m in meses), 2)
    total_despesas = round(sum(m['despesas'] for m in meses), 2)
    saldo_total = round(total_receitas - total_despesas, 2)
    return _resultado(
        {'por_mes': meses[:LIMITE_LINHAS], 'receitas_total': total_receitas,
         'despesas_total': total_despesas, 'saldo_total': saldo_total,
         'periodo': {'inicio': inicio.isoformat(), 'fim': fim.isoformat()}},
        destaques=[
            {'rotulo': 'Receitas', 'valor': _moeda(total_receitas)},
            {'rotulo': 'Despesas', 'valor': _moeda(total_despesas)},
            {'rotulo': 'Saldo', 'valor': _moeda(saldo_total), 'tom': 'positivo' if saldo_total >= 0 else 'critico'},
        ],
        tabela={
            'titulo': 'Fluxo financeiro mensal',
            'colunas': ['Mês', 'Receitas', 'Despesas', 'Saldo'],
            'linhas': [[m['mes'], _moeda(m['receitas']), _moeda(m['despesas']), _moeda(m['saldo'])]
                       for m in meses[:LIMITE_LINHAS]],
        } if meses else None,
        alertas=[
            {'nivel': 'critico', 'titulo': f"{m['mes']} fechou com saldo negativo de {_moeda(abs(m['saldo']))}"}
            for m in meses if m['saldo'] < 0
        ][:5],
    )


def custos_centro_custo(id_empresa, data_inicio=None, data_fim=None):
    despesas = [
        lancamento for lancamento in _lancamentos(id_empresa, data_inicio, data_fim)
        if lancamento.tipo == 'DESPESA'
    ]
    centros = {
        centro.id_centro_custo: centro.nome
        for centro in CentroCusto.query.all()
    }
    por_centro = defaultdict(float)
    for lancamento in despesas:
        nome = centros.get(lancamento.id_centro_custo, 'Sem centro de custo')
        por_centro[nome] += _num(lancamento.valor)
    ordenados = sorted(por_centro.items(), key=lambda item: item[1], reverse=True)
    total = sum(valor for _, valor in ordenados)
    return _resultado(
        {'total_despesas': round(total, 2),
         'por_centro_custo': {nome: round(valor, 2) for nome, valor in ordenados},
         'periodo': {'inicio': data_inicio, 'fim': data_fim}},
        destaques=[
            {'rotulo': 'Total de despesas', 'valor': _moeda(total), 'tom': 'atencao'},
        ] + ([{'rotulo': 'Maior centro de custo', 'valor': ordenados[0][0]}] if ordenados else []),
        tabela={
            'titulo': 'Despesas por centro de custo',
            'colunas': ['Centro de custo', 'Despesas'],
            'linhas': [[nome, _moeda(valor)] for nome, valor in ordenados[:LIMITE_LINHAS]],
        } if ordenados else None,
    )


def custo_por_hectare(id_empresa):
    propriedades = _ids_propriedades(id_empresa)
    safras = Safra.query.filter(Safra.id_propriedade.in_(propriedades)).all() if propriedades else []
    safras_por_id = {safra.id_safra: safra for safra in safras}
    despesas_por_safra = defaultdict(float)
    for lancamento in _lancamentos(id_empresa):
        if lancamento.tipo == 'DESPESA' and lancamento.id_safra in safras_por_id:
            despesas_por_safra[lancamento.id_safra] += _num(lancamento.valor)

    registros = []
    for id_safra, despesa in despesas_por_safra.items():
        safra = safras_por_id[id_safra]
        area = _num(safra.area_plantada)
        custo = round(despesa / area, 2) if area > 0 else None
        registros.append({
            'safra': safra.nome,
            'cultura': safra.cultura,
            'area_plantada_ha': round(area, 2) if area > 0 else None,
            'despesas': round(despesa, 2),
            'custo_por_hectare': custo,
        })
    registros.sort(
        key=lambda registro: registro['custo_por_hectare']
        if registro['custo_por_hectare'] is not None else -1,
        reverse=True,
    )
    linhas = [
        [
            registro['safra'],
            registro['cultura'],
            _area(registro['area_plantada_ha']) if registro['area_plantada_ha'] is not None
            else 'Área não informada',
            _moeda(registro['despesas']),
            f"{_moeda(registro['custo_por_hectare'])}/ha"
            if registro['custo_por_hectare'] is not None else 'Área não informada',
        ]
        for registro in registros[:LIMITE_LINHAS]
    ]
    destaques = []
    if registros and registros[0]['custo_por_hectare'] is not None:
        destaques.append({
            'rotulo': 'Custo por hectare',
            'valor': f"{_moeda(registros[0]['custo_por_hectare'])}/ha",
        })
    return _resultado(
        {'por_safra': registros[:LIMITE_LINHAS],
         'total_despesas': round(sum(registro['despesas'] for registro in registros), 2)},
        destaques=destaques,
        tabela={
            'titulo': 'Custo por hectare por safra',
            'colunas': ['Safra', 'Cultura', 'Área plantada', 'Despesas', 'Custo/ha'],
            'linhas': linhas,
        } if linhas else None,
    )


# Declaração das consultas para o LLM (function calling), limitadas pelos módulos do papel.
TOOLS = {
    'resumo_propriedades': {
        'funcao': resumo_propriedades, 'modulos': {'Propriedades'},
        'descricao': 'Quantidade de propriedades ativas da empresa, áreas totais/agricultáveis/de preservação/de pastagem e talhões ativos por propriedade.',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'area_disponivel': {
        'funcao': area_disponivel, 'modulos': {'Talhões'},
        'descricao': 'Talhões livres e ocupados, área disponível para plantio e simulação de plantar uma cultura em todos os talhões livres.',
        'parametros': {'type': 'object', 'properties': {
            'cultura': {'type': 'string', 'description': 'Cultura a simular nos talhões livres (opcional).'}}},
    },
    'safras': {
        'funcao': safras, 'modulos': {'Talhões', 'Atividades', 'Financeiro'},
        'descricao': 'Safras cadastradas, culturas e área plantada por cultura (base para análises de produtividade e planejamento).',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'estoque': {
        'funcao': estoque, 'modulos': {'Insumos'},
        'descricao': 'Situação do estoque de insumos, incluindo itens abaixo do estoque mínimo.',
        'parametros': {'type': 'object', 'properties': {
            'apenas_criticos': {'type': 'boolean', 'description': 'Somente itens no mínimo ou abaixo.'}}},
    },
    'lotes_a_vencer': {
        'funcao': lotes_a_vencer, 'modulos': {'Insumos'},
        'descricao': 'Lotes de insumos e fertilizantes vencidos ou a vencer, com valor estimado em risco.',
        'parametros': {'type': 'object', 'properties': {
            'dias': {'type': 'integer', 'description': 'Janela em dias a partir de hoje (padrão 30).'}}},
    },
    'atividades': {
        'funcao': atividades, 'modulos': {'Atividades'},
        'descricao': 'Atividades agrícolas por status, percentual concluído e atividades atrasadas.',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'funcionarios': {
        'funcao': funcionarios, 'modulos': {'Funcionários'},
        'descricao': 'Ranking de funcionários por atividades executadas e concluídas.',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'equipe': {
        'funcao': equipe, 'modulos': {'Funcionários'},
        'descricao': 'Quantidade de funcionários ativos por propriedade e cargo.',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'maquinas': {
        'funcao': maquinas, 'modulos': {'Atividades'},
        'descricao': 'Horas de uso e número de atividades por máquina, com custo somente para papéis com acesso financeiro.',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'consumo_insumos': {
        'funcao': consumo_insumos, 'modulos': {'Atividades', 'Insumos'},
        'descricao': 'Quantidade de insumos aplicados por produto e unidade, com filtro opcional por safra ou talhão; custo somente para papéis com acesso financeiro.',
        'parametros': {'type': 'object', 'properties': {
            'safra': {'type': 'string', 'description': 'Nome ou texto da safra (opcional).'},
            'talhao': {'type': 'string', 'description': 'Nome ou código do talhão (opcional).'},
        }},
    },
    'movimentacoes_estoque': {
        'funcao': movimentacoes_estoque, 'modulos': {'Insumos'},
        'descricao': 'Entradas e saídas de estoque por produto em um período (padrão 30 dias), com filtros de tipo e produto; valores de compra somente para papéis com acesso financeiro.',
        'parametros': {'type': 'object', 'properties': {
            'dias': {'type': 'integer', 'description': 'Número de dias do período (padrão 30).'},
            'tipo': {'type': 'string', 'enum': ['ENTRADA', 'SAIDA']},
            'produto': {'type': 'string', 'description': 'Filtro parcial pelo nome do produto.'},
        }},
    },
    'fornecedores': {
        'funcao': fornecedores, 'modulos': {'Insumos'},
        'descricao': 'Fornecedores com entradas de estoque na empresa, ordenados pela quantidade de entradas e data da última; valores comprados somente para papéis com acesso financeiro.',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'custos': {
        'funcao': custos, 'modulos': {'Financeiro'},
        'descricao': 'Despesas por categoria em um período (ex.: gastos com fertilizantes no mês).',
        'parametros': {'type': 'object', 'properties': {
            'data_inicio': {'type': 'string', 'description': 'Data inicial AAAA-MM-DD.'},
            'data_fim': {'type': 'string', 'description': 'Data final AAAA-MM-DD.'},
            'categoria': {'type': 'string', 'description': 'Filtro por categoria ou descrição (ex.: fertilizante).'}}},
    },
    'lucro_safra': {
        'funcao': lucro_safra, 'modulos': {'Financeiro'},
        'descricao': 'Receitas, despesas e lucro por safra.',
        'parametros': {'type': 'object', 'properties': {}},
    },
    'fluxo_mensal': {
        'funcao': fluxo_mensal, 'modulos': {'Financeiro'},
        'descricao': 'Receitas, despesas e saldo por mês, com período opcional (padrão: últimos 12 meses).',
        'parametros': {'type': 'object', 'properties': {
            'data_inicio': {'type': 'string', 'description': 'Data inicial AAAA-MM-DD (opcional).'},
            'data_fim': {'type': 'string', 'description': 'Data final AAAA-MM-DD (opcional).'},
        }},
    },
    'custos_centro_custo': {
        'funcao': custos_centro_custo, 'modulos': {'Financeiro'},
        'descricao': 'Despesas da empresa por centro de custo, com filtro opcional de período; despesas sem vínculo são agrupadas como Sem centro de custo.',
        'parametros': {'type': 'object', 'properties': {
            'data_inicio': {'type': 'string', 'description': 'Data inicial AAAA-MM-DD (opcional).'},
            'data_fim': {'type': 'string', 'description': 'Data final AAAA-MM-DD (opcional).'},
        }},
    },
    'custo_por_hectare': {
        'funcao': custo_por_hectare, 'modulos': {'Financeiro'},
        'descricao': 'Despesas por safra divididas pela área plantada; safras sem área informada são destacadas.',
        'parametros': {'type': 'object', 'properties': {}},
    },
}


def tools_permitidas(perfil):
    from services.safra_ia.permissoes import modulos_do_papel

    modulos = modulos_do_papel(perfil)
    return {nome: t for nome, t in TOOLS.items() if t['modulos'] & modulos}


def executar_tool(nome, argumentos, id_empresa, perfil):
    from services.safra_ia.permissoes import modulos_do_papel, ve_financeiro

    tool = TOOLS.get(nome)
    if tool is None:
        return {'erro': f'Consulta desconhecida: {nome}'}
    if not (tool['modulos'] & modulos_do_papel(perfil)):
        modulo = ', '.join(sorted(tool['modulos']))
        return {'erro': f'Seu papel não tem acesso ao módulo {modulo}.'}
    permitidos = set(tool['parametros']['properties'])
    kwargs = {k: v for k, v in (argumentos or {}).items() if k in permitidos and v not in (None, '')}
    if 'ver_valores' in signature(tool['funcao']).parameters:
        kwargs['ver_valores'] = ve_financeiro(perfil)
    try:
        return tool['funcao'](id_empresa, **kwargs)
    except (ValueError, TypeError) as exc:
        return {'erro': f'Parâmetros inválidos: {exc}'}
