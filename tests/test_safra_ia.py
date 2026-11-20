import datetime

import pytest

from models import db
from models.categoria_insumo import CategoriaInsumo
from models.empresa_agricola import EmpresaAgricola
from models.insumo import Insumo
from models.lancamento_financeiro import LancamentoFinanceiro
from models.lote_insumo import LoteInsumo
from models.produto import Produto
from models.propriedade import Propriedade
from models.talhao import Talhao
from models.usuario import Usuario
from services.auth_service import AuthService
from services.safra_ia import tools
from services.safra_ia.gemini_client import ErroLLM


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
    assert 'NÃO tem acesso a dados financeiros' in falso.sistema
    assert 'destaques' not in resp.get_json()


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
