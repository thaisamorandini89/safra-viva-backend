import datetime

import pytest

from models import db
from models.atividade_agricola import AtividadeAgricola
from models.atividade_insumo import AtividadeInsumo
from models.atividade_maquina import AtividadeMaquina
from models.categoria_atividade import CategoriaAtividade
from models.categoria_insumo import CategoriaInsumo
from models.centro_custo import CentroCusto
from models.empresa_agricola import EmpresaAgricola
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
from models.tipo_atividade import TipoAtividade
from models.usuario import Usuario
from services.auth_service import AuthService
from services.safra_ia import tools
from services.safra_ia.gemini_client import ErroLLM
from services.safra_ia.permissoes import modulos_do_papel, papel_do_perfil, ve_financeiro


def test_matriz_de_papeis_tem_fallback_restrito():
    assert papel_do_perfil(' Visitante ') == 'colaborador'
    assert modulos_do_papel('visitante') == set()
    assert modulos_do_papel('financeiro') == {'Financeiro'}
    assert ve_financeiro('gerente-agricola')
    assert not ve_financeiro('agronomo')


def test_tools_liberadas_seguem_modulos_do_papel():
    assert 'custos' not in tools.tools_permitidas('agronomo')
    assert 'estoque' not in tools.tools_permitidas('financeiro')
    assert 'atividades' in tools.tools_permitidas('operador')
    assert 'resumo_propriedades' not in tools.tools_permitidas('visitante')


def test_tool_negada_nao_e_executada(monkeypatch):
    monkeypatch.setitem(
        tools.TOOLS['atividades'],
        'funcao',
        lambda *_args, **_kwargs: pytest.fail('A tool negada não deve executar'),
    )
    resultado = tools.executar_tool('atividades', {}, 1, 'financeiro')
    assert 'não tem acesso' in resultado['erro']


def _empresa(cnpj):
    e = EmpresaAgricola(razao_social=f'Fazenda {cnpj}', cnpj=cnpj)
    db.session.add(e)
    db.session.flush()
    p = Propriedade(nome_propriedade='Sede', id_empresa=e.id_empresa, car='CAR', latitude=-15, longitude=-47,
                    area_total=100, area_agricultavel=80, area_preservacao=20)
    db.session.add(p)
    db.session.flush()
    return e, p


@pytest.fixture()
def dados(app):
    e1, p1 = _empresa('11111111000111')
    e2, p2 = _empresa('22222222000122')
    db.session.add_all([
        Talhao(nome_talhao='Norte', codigo_talhao='T-01', id_propriedade=p1.id_propriedade, area_total=30,
               area_utilizavel=28, status_inicial='Livre'),
        Talhao(nome_talhao='Sul', codigo_talhao='T-02', id_propriedade=p1.id_propriedade, area_total=20,
               status_inicial='Ocupado'),
        Talhao(nome_talhao='Outra', codigo_talhao='X-01', id_propriedade=p2.id_propriedade, area_total=500,
               status_inicial='Livre'),
    ])
    cat = CategoriaInsumo(nome_categoria='Fertilizante')
    db.session.add(cat)
    db.session.flush()
    prod = Produto(nome_produto='NPK 10-10-10', unidade_medida='kg',
                   id_categoria_insumo=cat.id_categoria_insumo)
    db.session.add(prod)
    db.session.flush()
    ins = Insumo(id_produto=prod.id_produto, id_propriedade=p1.id_propriedade, estoque_atual=5,
                 estoque_minimo=10, valor_unitario=4)
    db.session.add(ins)
    db.session.flush()
    db.session.add(LoteInsumo(id_insumo=ins.id_insumo, numero_lote='L1', quantidade=5,
                              data_validade=datetime.date.today() + datetime.timedelta(days=10)))
    hoje = datetime.date.today()
    db.session.add_all([
        LancamentoFinanceiro(tipo='DESPESA', categoria='Fertilizantes', valor=1500, data_lancamento=hoje,
                             id_empresa=e1.id_empresa),
        LancamentoFinanceiro(tipo='RECEITA', categoria='Venda', valor=5000, data_lancamento=hoje,
                             id_empresa=e1.id_empresa),
        LancamentoFinanceiro(tipo='DESPESA', categoria='Fertilizantes', valor=99999, data_lancamento=hoje,
                             id_empresa=e2.id_empresa),
    ])
    db.session.commit()
    AuthService.garantir_usuarios_demo(e1.id_empresa)
    return e1


class GeminiFalso:
    """Simula o function calling: chama as tools pedidas e devolve um texto fixo."""

    def __init__(self, pedidos):
        self.pedidos = pedidos
        self.declaracoes = None
        self.sistema = None

    def conversar(self, sistema, pergunta, declaracoes, executar):
        self.sistema, self.declaracoes = sistema, declaracoes
        chamadas = [(n, a, executar(n, a)) for n, a in self.pedidos]
        return 'Resposta redigida pelo modelo.', chamadas


def _token(perfil):
    return AuthService.gerar_token(Usuario.query.filter_by(perfil=perfil).first())


def _consultar(app, client, perfil, pedidos, pergunta='pergunta'):
    falso = GeminiFalso(pedidos)
    app.config['SAFRAIA_CLIENTE_FACTORY'] = lambda: falso
    resp = client.post('/api/safra-ia/consultar', json={'pergunta': pergunta},
                       headers={'Authorization': f'Bearer {_token(perfil)}'})
    return resp, falso


def test_sem_login_401(client):
    assert client.post('/api/safra-ia/consultar', json={'pergunta': 'oi'}).status_code == 401


def test_perfil_safra_ia_autenticado_por_papel(app, client, dados):
    headers = {'Authorization': f'Bearer {_token("estoquista")}'}
    resp = client.get('/api/safra-ia/perfil', headers=headers)
    corpo = resp.get_json()
    assert resp.status_code == 200
    assert corpo['papel'] == 'estoquista'
    assert corpo['nome_papel'] == 'Estoquista'
    assert {'estoque', 'lotes_a_vencer', 'atividades'} <= {
        consulta['nome'] for consulta in corpo['consultas']
    }
    assert 'custos' not in {consulta['nome'] for consulta in corpo['consultas']}


def test_perfil_gerente_agricola_tem_consultas_financeiras(app, client, dados):
    usuario = Usuario(
        nome='Gerente de teste',
        email='gerente@safraviva.test',
        senha_hash='hash',
        perfil='gerente-agricola',
        id_empresa=dados.id_empresa,
    )
    db.session.add(usuario)
    db.session.commit()
    headers = {'Authorization': f'Bearer {AuthService.gerar_token(usuario)}'}
    resp = client.get('/api/safra-ia/perfil', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['papel'] == 'gerente-agricola'
    assert 'custos' in {consulta['nome'] for consulta in resp.get_json()['consultas']}


def test_perfil_safra_ia_sem_login_401(client):
    assert client.get('/api/safra-ia/perfil').status_code == 401


def test_pergunta_vazia_422(app, client, dados):
    resp = client.post('/api/safra-ia/consultar', json={'pergunta': '  '},
                       headers={'Authorization': f'Bearer {_token("administrador")}'})
    assert resp.status_code == 422


def test_area_disponivel_isolada_por_empresa(app, client, dados):
    resp, _ = _consultar(app, client, 'agronomo', [('area_disponivel', {'cultura': 'soja'})])
    corpo = resp.get_json()
    assert resp.status_code == 200
    assert corpo['origem'] == 'backend'
    assert corpo['intent'] == 'area_disponivel'
    assert corpo['texto'] == 'Resposta redigida pelo modelo.'
    assert corpo['destaques'][0]['valor'] == '28,00 ha'
    assert all(linha[0] != 'X-01' for linha in corpo['tabela']['linhas'])


def test_agronomo_nao_recebe_tools_financeiras(app, client, dados):
    resp, falso = _consultar(app, client, 'agronomo', [('custos', {})])
    assert 'custos' not in falso.declaracoes
    assert 'lucro_safra' not in falso.declaracoes
    assert 'Financeiro' in falso.sistema
    assert 'não visualiza' in falso.sistema
    assert 'destaques' not in resp.get_json()


def test_papel_da_consulta_vem_do_login_e_ignora_persona(app, client, dados):
    falso = GeminiFalso([('area_disponivel', {})])
    app.config['SAFRAIA_CLIENTE_FACTORY'] = lambda: falso
    resp = client.post(
        '/api/safra-ia/consultar',
        json={'pergunta': 'Quantas áreas?', 'persona': 'administrador', 'papel': 'administrador'},
        headers={'Authorization': f'Bearer {_token("estoquista")}'},
    )
    corpo = resp.get_json()
    assert resp.status_code == 200
    assert corpo['papel'] == 'estoquista'
    assert 'persona' not in corpo
    assert 'area_disponivel' not in falso.declaracoes
    assert 'administrador' not in falso.sistema.lower()


def test_prompt_reconhece_administrador_da_fazenda(app, client, dados):
    resp, falso = _consultar(app, client, 'administrador', [])
    assert resp.get_json()['papel'] == 'administrador'
    assert 'Administrador' in falso.sistema
    assert 'administrador da fazenda' in falso.sistema.lower()


def test_custos_para_financeiro_somente_da_empresa(app, client, dados):
    resp, falso = _consultar(app, client, 'financeiro', [('custos', {'categoria': 'fertiliz'})])
    corpo = resp.get_json()
    assert 'custos' in falso.declaracoes
    assert corpo['destaques'][0]['valor'] == 'R$ 1.500,00'


def test_estoque_e_validade_geram_alertas(app, dados):
    estoque = tools.estoque(dados.id_empresa, apenas_criticos=True)
    assert estoque['dados']['itens_criticos'] == 1
    lotes = tools.lotes_a_vencer(dados.id_empresa, dias=30)
    assert lotes['dados']['valor_em_risco'] == 20.0
    assert lotes['alertas'][0]['nivel'] == 'alerta'


def test_resumo_propriedades_conta_ativas_e_somente_da_empresa(app, dados):
    p_ativa = Propriedade(
        nome_propriedade='Lavoura',
        id_empresa=dados.id_empresa,
        car='CAR-ATIVA',
        latitude=-15,
        longitude=-47,
        area_total=50,
        area_agricultavel=40,
        area_preservacao=10,
        area_pastagem=5,
    )
    p_inativa = Propriedade(
        nome_propriedade='Inativa',
        id_empresa=dados.id_empresa,
        car='CAR-INATIVA',
        latitude=-15,
        longitude=-47,
        area_total=90,
        area_agricultavel=70,
        area_preservacao=20,
        status=False,
    )
    db.session.add_all([p_ativa, p_inativa])
    db.session.flush()
    db.session.add_all([
        Talhao(nome_talhao='Ativo', codigo_talhao='A-01', id_propriedade=p_ativa.id_propriedade,
               area_total=10, status=True),
        Talhao(nome_talhao='Desativado', codigo_talhao='A-02', id_propriedade=p_ativa.id_propriedade,
               area_total=10, status=False),
    ])
    db.session.commit()

    resultado = tools.resumo_propriedades(dados.id_empresa)
    assert resultado['dados']['propriedades_ativas'] == 2
    assert resultado['dados']['area_total_ha'] == 150
    assert resultado['dados']['talhoes_ativos'] == 3
    assert len(resultado['tabela']['linhas']) == 2
    assert all(linha[0] != 'Outra' for linha in resultado['tabela']['linhas'])


def test_resumo_propriedades_sem_propriedades(app):
    empresa = EmpresaAgricola(razao_social='Sem propriedade', cnpj='33333333000133')
    db.session.add(empresa)
    db.session.commit()
    resultado = tools.resumo_propriedades(empresa.id_empresa)
    assert resultado['dados']['propriedades_ativas'] == 0
    assert resultado['tabela'] is None


def test_equipe_ignora_funcionario_inativo_desligado_ou_de_outra_empresa(app, dados):
    p1 = Propriedade.query.filter_by(id_empresa=dados.id_empresa).first()
    p2 = Propriedade.query.filter(Propriedade.id_empresa != dados.id_empresa).first()
    ativos = [
        Funcionario(nome_completo='Ativo', cpf='10000000001', cargo='Operador', data_admissao=datetime.date.today()),
        Funcionario(nome_completo='Desligado', cpf='10000000002', cargo='Operador',
                    data_admissao=datetime.date.today(), data_desligamento=datetime.date.today()),
        Funcionario(nome_completo='Inativo', cpf='10000000003', cargo='Operador',
                    data_admissao=datetime.date.today(), status=False),
        Funcionario(nome_completo='Outra empresa', cpf='10000000004', cargo='Gerente',
                    data_admissao=datetime.date.today()),
    ]
    db.session.add_all(ativos)
    db.session.flush()
    db.session.add_all([
        FuncionarioPropriedade(id_funcionario=ativos[0].id_funcionario, id_propriedade=p1.id_propriedade),
        FuncionarioPropriedade(id_funcionario=ativos[1].id_funcionario, id_propriedade=p1.id_propriedade),
        FuncionarioPropriedade(id_funcionario=ativos[2].id_funcionario, id_propriedade=p1.id_propriedade),
        FuncionarioPropriedade(id_funcionario=ativos[3].id_funcionario, id_propriedade=p2.id_propriedade),
    ])
    db.session.commit()

    resultado = tools.equipe(dados.id_empresa)
    assert resultado['dados']['total_funcionarios'] == 1
    assert resultado['tabela']['linhas'] == [['Sede', 'Operador', 1]]


def test_maquinas_isoladas_por_empresa_e_valores_restritos(app, dados):
    p1 = Propriedade.query.filter_by(id_empresa=dados.id_empresa).first()
    p2 = Propriedade.query.filter(Propriedade.id_empresa != dados.id_empresa).first()
    t1 = Talhao.query.filter_by(id_propriedade=p1.id_propriedade).first()
    t2 = Talhao.query.filter_by(id_propriedade=p2.id_propriedade).first()
    categoria = CategoriaAtividade(nome='Operação')
    db.session.add(categoria)
    db.session.flush()
    tipo = TipoAtividade(descricao='Preparo', id_categoria_atividade=categoria.id_categoria_atividade)
    maquina = Maquina(nome='Trator da empresa')
    maquina_outra = Maquina(nome='Trator de outra empresa')
    db.session.add_all([tipo, maquina, maquina_outra])
    db.session.flush()
    atividades = [
        AtividadeAgricola(id_categoria_atividade=categoria.id_categoria_atividade,
                          id_tipo_atividade=tipo.id_atividade, id_talhao=t1.id_talhao,
                          id_propriedade=p1.id_propriedade, data_inicio=datetime.date.today()),
        AtividadeAgricola(id_categoria_atividade=categoria.id_categoria_atividade,
                          id_tipo_atividade=tipo.id_atividade, id_talhao=t1.id_talhao,
                          id_propriedade=p1.id_propriedade, data_inicio=datetime.date.today()),
        AtividadeAgricola(id_categoria_atividade=categoria.id_categoria_atividade,
                          id_tipo_atividade=tipo.id_atividade, id_talhao=t2.id_talhao,
                          id_propriedade=p2.id_propriedade, data_inicio=datetime.date.today()),
    ]
    db.session.add_all(atividades)
    db.session.flush()
    db.session.add_all([
        AtividadeMaquina(id_atividade_agricola=atividades[0].id_atividade_agricola,
                         id_maquina=maquina.id_maquina, horas=2, custo=20),
        AtividadeMaquina(id_atividade_agricola=atividades[1].id_atividade_agricola,
                         id_maquina=maquina.id_maquina, horas=3, custo=30),
        AtividadeMaquina(id_atividade_agricola=atividades[2].id_atividade_agricola,
                         id_maquina=maquina_outra.id_maquina, horas=99, custo=999),
    ])
    db.session.commit()

    operacional = tools.executar_tool('maquinas', {}, dados.id_empresa, 'supervisor-campo')
    financeiro = tools.executar_tool('maquinas', {}, dados.id_empresa, 'gerente-agricola')
    assert operacional['dados']['total_maquinas'] == 1
    assert 'custo_total' not in operacional['dados']['maquinas'][0]
    assert 'Custo' not in operacional['tabela']['colunas']
    assert financeiro['dados']['maquinas'][0]['custo_total'] == 50
    assert financeiro['tabela']['linhas'][0][-1] == 'R$ 50,00'


def test_consumo_insumos_filtra_safra_talhao_e_restringe_custos(app, dados):
    p1 = Propriedade.query.filter_by(id_empresa=dados.id_empresa).first()
    p2 = Propriedade.query.filter(Propriedade.id_empresa != dados.id_empresa).first()
    t1 = Talhao.query.filter_by(id_propriedade=p1.id_propriedade).first()
    t2 = Talhao.query.filter_by(id_propriedade=p1.id_propriedade).order_by(Talhao.id_talhao.desc()).first()
    t3 = Talhao.query.filter_by(id_propriedade=p2.id_propriedade).first()
    insumo_p1 = Insumo.query.filter_by(id_propriedade=p1.id_propriedade).first()
    categoria = CategoriaAtividade(nome='Aplicação')
    db.session.add(categoria)
    db.session.flush()
    tipo = TipoAtividade(descricao='Adubação', id_categoria_atividade=categoria.id_categoria_atividade)
    db.session.add(tipo)
    db.session.flush()
    atividades = [
        AtividadeAgricola(id_categoria_atividade=categoria.id_categoria_atividade,
                          id_tipo_atividade=tipo.id_atividade, id_talhao=t1.id_talhao,
                          id_propriedade=p1.id_propriedade, safra='Safra 2025/2026',
                          data_inicio=datetime.date.today()),
        AtividadeAgricola(id_categoria_atividade=categoria.id_categoria_atividade,
                          id_tipo_atividade=tipo.id_atividade, id_talhao=t2.id_talhao,
                          id_propriedade=p1.id_propriedade, safra='Safra 2024/2025',
                          data_inicio=datetime.date.today()),
        AtividadeAgricola(id_categoria_atividade=categoria.id_categoria_atividade,
                          id_tipo_atividade=tipo.id_atividade, id_talhao=t3.id_talhao,
                          id_propriedade=p2.id_propriedade, safra='Safra 2025/2026',
                          data_inicio=datetime.date.today()),
    ]
    db.session.add_all(atividades)
    db.session.flush()
    insumo_p2 = Insumo(id_produto=insumo_p1.id_produto, id_propriedade=p2.id_propriedade,
                       estoque_atual=0, estoque_minimo=0, valor_unitario=4)
    db.session.add(insumo_p2)
    db.session.flush()
    db.session.add_all([
        AtividadeInsumo(id_atividade_agricola=atividades[0].id_atividade_agricola,
                        id_insumo=insumo_p1.id_insumo, quantidade=5, unidade='kg', custo=25),
        AtividadeInsumo(id_atividade_agricola=atividades[1].id_atividade_agricola,
                        id_insumo=insumo_p1.id_insumo, quantidade=7, unidade='kg', custo=35),
        AtividadeInsumo(id_atividade_agricola=atividades[2].id_atividade_agricola,
                        id_insumo=insumo_p2.id_insumo, quantidade=99, unidade='kg', custo=999),
    ])
    db.session.commit()

    argumentos = {'safra': '2025/2026', 'talhao': t1.codigo_talhao}
    agronomo = tools.executar_tool('consumo_insumos', argumentos, dados.id_empresa, 'agronomo')
    administrador = tools.executar_tool('consumo_insumos', argumentos, dados.id_empresa, 'administrador')
    assert agronomo['dados']['itens'] == [{'produto': 'NPK 10-10-10', 'quantidade': 5.0, 'unidade': 'kg'}]
    assert 'custo_total' not in agronomo['dados']['itens'][0]
    assert 'Custo' not in agronomo['tabela']['colunas']
    assert administrador['dados']['itens'][0]['custo_total'] == 25
    assert administrador['tabela']['linhas'][0][-1] == 'R$ 25,00'


def test_movimentacoes_respeitam_periodo_tipo_produto_e_empresa(app, dados):
    p2 = Propriedade.query.filter(Propriedade.id_empresa != dados.id_empresa).first()
    insumo_p1 = Insumo.query.filter_by(id_propriedade=Propriedade.query.filter_by(
        id_empresa=dados.id_empresa
    ).first().id_propriedade).first()
    insumo_p2 = Insumo(id_produto=insumo_p1.id_produto, id_propriedade=p2.id_propriedade,
                       estoque_atual=0, estoque_minimo=0, valor_unitario=4)
    db.session.add(insumo_p2)
    db.session.flush()
    agora = datetime.datetime.now()
    db.session.add_all([
        MovimentacaoEstoque(id_insumo=insumo_p1.id_insumo, tipo_movimentacao='SAIDA',
                            quantidade=3, valor_unitario=4, data_movimentacao=agora),
        MovimentacaoEstoque(id_insumo=insumo_p1.id_insumo, tipo_movimentacao='ENTRADA',
                            quantidade=10, valor_unitario=5, data_movimentacao=agora),
        MovimentacaoEstoque(id_insumo=insumo_p1.id_insumo, tipo_movimentacao='SAIDA',
                            quantidade=7, valor_unitario=4,
                            data_movimentacao=agora - datetime.timedelta(days=45)),
        MovimentacaoEstoque(id_insumo=insumo_p2.id_insumo, tipo_movimentacao='SAIDA',
                            quantidade=99, valor_unitario=4, data_movimentacao=agora),
    ])
    db.session.commit()

    args = {'tipo': 'SAIDA', 'produto': 'NPK'}
    estoquista = tools.executar_tool('movimentacoes_estoque', args, dados.id_empresa, 'estoquista')
    administrador = tools.executar_tool('movimentacoes_estoque', args, dados.id_empresa, 'administrador')
    assert estoquista['dados']['total_movimentacoes'] == 1
    assert estoquista['dados']['itens'][0]['quantidade'] == 3
    assert 'valor_total' not in estoquista['dados']['itens'][0]
    assert administrador['dados']['itens'][0]['valor_total'] == 12


def test_estoquista_pergunta_sobre_fornecedores(app, client, dados):
    p1 = Propriedade.query.filter_by(id_empresa=dados.id_empresa).first()
    p2 = Propriedade.query.filter(Propriedade.id_empresa != dados.id_empresa).first()
    insumo_p1 = Insumo.query.filter_by(id_propriedade=p1.id_propriedade).first()
    insumo_p2 = Insumo(id_produto=insumo_p1.id_produto, id_propriedade=p2.id_propriedade,
                       estoque_atual=0, estoque_minimo=0, valor_unitario=5)
    fornecedor = Fornecedor(nome_fornecedor='Fornecedor da empresa')
    fornecedor_outra = Fornecedor(nome_fornecedor='Fornecedor de outra empresa')
    db.session.add_all([insumo_p2, fornecedor, fornecedor_outra])
    db.session.flush()
    agora = datetime.datetime.now()
    db.session.add_all([
        MovimentacaoEstoque(id_insumo=insumo_p1.id_insumo, id_fornecedor=fornecedor.id_fornecedor,
                            tipo_movimentacao='ENTRADA', quantidade=10, valor_unitario=4,
                            data_movimentacao=agora - datetime.timedelta(days=1)),
        MovimentacaoEstoque(id_insumo=insumo_p1.id_insumo, id_fornecedor=fornecedor.id_fornecedor,
                            tipo_movimentacao='ENTRADA', quantidade=5, valor_unitario=4,
                            data_movimentacao=agora),
        MovimentacaoEstoque(id_insumo=insumo_p2.id_insumo, id_fornecedor=fornecedor_outra.id_fornecedor,
                            tipo_movimentacao='ENTRADA', quantidade=100, valor_unitario=5,
                            data_movimentacao=agora),
    ])
    db.session.commit()

    estoque = tools.executar_tool('fornecedores', {}, dados.id_empresa, 'estoquista')
    financeiro = tools.executar_tool('fornecedores', {}, dados.id_empresa, 'gerente-agricola')
    assert estoque['dados']['total_fornecedores'] == 1
    assert estoque['dados']['fornecedores'][0]['fornecedor'] == 'Fornecedor da empresa'
    assert estoque['dados']['fornecedores'][0]['entradas'] == 2
    assert 'valor_comprado' not in estoque['dados']['fornecedores'][0]
    assert financeiro['dados']['fornecedores'][0]['valor_comprado'] == 60
    resp, falso = _consultar(app, client, 'estoquista', [('fornecedores', {})],
                             pergunta='Quais fornecedores mais entregaram?')
    assert resp.status_code == 200
    assert 'fornecedores' in falso.declaracoes
    assert resp.get_json()['tabela']['titulo'] == 'Fornecedores por entradas'


def test_fluxo_mensal_destaca_mes_com_saldo_negativo(app, dados):
    hoje = datetime.date.today()
    db.session.add(LancamentoFinanceiro(
        tipo='DESPESA',
        categoria='Operação',
        valor=6000,
        data_lancamento=hoje,
        id_empresa=dados.id_empresa,
    ))
    db.session.commit()
    inicio = hoje.replace(day=1)
    resultado = tools.executar_tool(
        'fluxo_mensal',
        {'data_inicio': inicio.isoformat(), 'data_fim': hoje.isoformat()},
        dados.id_empresa,
        'financeiro',
    )
    assert resultado['dados']['receitas_total'] == 5000
    assert resultado['dados']['despesas_total'] == 7500
    assert resultado['dados']['saldo_total'] == -2500
    assert resultado['alertas'][0]['nivel'] == 'critico'
    assert resultado['alertas'][0]['titulo'].startswith(hoje.strftime('%Y-%m'))


def test_custos_centro_custo_agrupa_sem_centro_e_isola_empresa(app, dados):
    hoje = datetime.date.today()
    operacional = CentroCusto(nome='Operacional', tipo='OPERACIONAL')
    administrativo = CentroCusto(nome='Administrativo', tipo='ADMINISTRATIVO')
    db.session.add_all([operacional, administrativo])
    db.session.flush()
    empresa_outra = EmpresaAgricola.query.filter(EmpresaAgricola.id_empresa != dados.id_empresa).first()
    db.session.add_all([
        LancamentoFinanceiro(tipo='DESPESA', categoria='Insumos', valor=50, data_lancamento=hoje,
                             id_empresa=dados.id_empresa, id_centro_custo=operacional.id_centro_custo),
        LancamentoFinanceiro(tipo='DESPESA', categoria='Salários', valor=100, data_lancamento=hoje,
                             id_empresa=dados.id_empresa, id_centro_custo=administrativo.id_centro_custo),
        LancamentoFinanceiro(tipo='DESPESA', categoria='Diversos', valor=25, data_lancamento=hoje,
                             id_empresa=dados.id_empresa),
        LancamentoFinanceiro(tipo='DESPESA', categoria='Outro', valor=9999, data_lancamento=hoje,
                             id_empresa=empresa_outra.id_empresa, id_centro_custo=administrativo.id_centro_custo),
    ])
    db.session.commit()

    resultado = tools.executar_tool('custos_centro_custo', {}, dados.id_empresa, 'financeiro')
    assert resultado['dados']['total_despesas'] == 1675
    assert resultado['dados']['por_centro_custo'] == {
        'Administrativo': 100,
        'Sem centro de custo': 1525,
        'Operacional': 50,
    }
    assert resultado['tabela']['linhas'][0] == ['Sem centro de custo', 'R$ 1.525,00']


def test_custo_por_hectare_mostra_safra_sem_area_e_isola_empresa(app, dados):
    hoje = datetime.date.today()
    propriedade = Propriedade.query.filter_by(id_empresa=dados.id_empresa).first()
    empresa_outra = EmpresaAgricola.query.filter(EmpresaAgricola.id_empresa != dados.id_empresa).first()
    propriedade_outra = Propriedade.query.filter_by(id_empresa=empresa_outra.id_empresa).first()
    com_area = Safra(nome='Soja 25/26', cultura='Soja', id_propriedade=propriedade.id_propriedade,
                     data_inicio=hoje, area_plantada=100)
    sem_area = Safra(nome='Milho 25/26', cultura='Milho', id_propriedade=propriedade.id_propriedade,
                     data_inicio=hoje)
    outra_empresa = Safra(nome='Outra safra', cultura='Soja', id_propriedade=propriedade_outra.id_propriedade,
                          data_inicio=hoje, area_plantada=20)
    db.session.add_all([com_area, sem_area, outra_empresa])
    db.session.flush()
    db.session.add_all([
        LancamentoFinanceiro(tipo='DESPESA', categoria='Insumos', valor=50000, data_lancamento=hoje,
                             id_empresa=dados.id_empresa, id_safra=com_area.id_safra),
        LancamentoFinanceiro(tipo='DESPESA', categoria='Insumos', valor=2000, data_lancamento=hoje,
                             id_empresa=dados.id_empresa, id_safra=sem_area.id_safra),
        LancamentoFinanceiro(tipo='DESPESA', categoria='Insumos', valor=9999, data_lancamento=hoje,
                             id_empresa=empresa_outra.id_empresa, id_safra=outra_empresa.id_safra),
    ])
    db.session.commit()

    resultado = tools.executar_tool('custo_por_hectare', {}, dados.id_empresa, 'financeiro')
    por_safra = {item['safra']: item for item in resultado['dados']['por_safra']}
    assert por_safra['Soja 25/26']['custo_por_hectare'] == 500
    assert por_safra['Milho 25/26']['custo_por_hectare'] is None
    assert resultado['dados']['total_despesas'] == 52000
    assert 'Área não informada' in resultado['tabela']['linhas'][1]
    assert 'Outra safra' not in por_safra


def test_falha_do_llm_propaga_status(app, client, dados):
    class Quebrado:
        def conversar(self, *a):
            raise ErroLLM('Limite de uso do Gemini atingido.', status=429)

    app.config['SAFRAIA_CLIENTE_FACTORY'] = lambda: Quebrado()
    resp = client.post('/api/safra-ia/consultar', json={'pergunta': 'oi'},
                       headers={'Authorization': f'Bearer {_token("administrador")}'})
    assert resp.status_code == 429
    assert 'Gemini' in resp.get_json()['error']


def test_rate_limit_por_usuario(app, client, dados):
    from controllers.safra_ia_controller import _chamadas_por_usuario
    _chamadas_por_usuario.clear()
    app.config['SAFRAIA_LIMITE_MINUTO'] = 2
    codigos = [_consultar(app, client, 'estoquista', [])[0].status_code for _ in range(3)]
    assert codigos == [200, 200, 429]
