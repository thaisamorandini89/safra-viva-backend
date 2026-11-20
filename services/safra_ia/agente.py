import datetime

from flask import current_app

from services.safra_ia import tools as tools_mod
from services.safra_ia.gemini_client import ClienteGemini
from services.safra_ia.permissoes import persona_do_perfil, pode_ver_financeiro

SUGESTOES = {
    'produtor': ['Quantos hectares ainda estão disponíveis para plantio?', 'Qual o lucro por safra?',
                 'Algum insumo está vencendo?'],
    'agronomo': ['Quais insumos estão abaixo do estoque mínimo?', 'Qual a recomendação geral para rotação após soja?',
                 'Quantas atividades estão atrasadas?'],
    'administrador': ['Quanto gastei com fertilizantes este mês?', 'Qual o lucro por safra?',
                      'Quais lotes vencem nos próximos 30 dias?'],
    'gerente': ['Qual funcionário realizou mais atividades?', 'Quantas atividades estão atrasadas?',
                'Quais insumos estão abaixo do estoque mínimo?'],
}


def _sistema(usuario, financeiro):
    hoje = datetime.date.today().isoformat()
    restricao = '' if financeiro else (
        ' O perfil deste usuário NÃO tem acesso a dados financeiros: se pedirem custos, receitas, lucro ou '
        'orçamento, explique educadamente que é necessário um perfil financeiro ou administrador.')
    return (
        'Você é o SafraIA, assistente do sistema de gestão rural SafraViva. Responda em português do Brasil, '
        'de forma objetiva (até 5 frases), em texto simples sem markdown (sem asteriscos ou #), para o usuário '
        f'{usuario.nome} (perfil {usuario.perfil}). Hoje é {hoje}. '
        'REGRAS: use SEMPRE as funções disponíveis para obter números da fazenda; nunca invente valores, '
        'percentuais, nomes ou datas que não vieram das funções. Se a função retornar vazio, diga que não há '
        'dados cadastrados e sugira o que cadastrar. A tabela e os indicadores já são exibidos ao usuário, então '
        'resuma e interprete em vez de repetir tudo. Para dúvidas agronômicas gerais (rotação, adubação, manejo '
        'de solo) responda com boas práticas gerais e avise que é orientação geral, que não substitui um '
        'agrônomo responsável. Recuse assuntos fora de gestão rural.' + restricao
    )


def _criar_cliente():
    fabrica = current_app.config.get('SAFRAIA_CLIENTE_FACTORY')
    return fabrica() if fabrica else ClienteGemini()


def consultar(usuario, pergunta):
    financeiro = pode_ver_financeiro(usuario.perfil)
    persona = persona_do_perfil(usuario.perfil)
    permitidas = tools_mod.tools_permitidas(financeiro)

    def executar(nome, args):
        resultado = tools_mod.executar_tool(nome, args, usuario.id_empresa, financeiro)
        return resultado

    cliente = _criar_cliente()
    texto, chamadas = cliente.conversar(
        _sistema(usuario, financeiro),
        pergunta,
        {n: {'descricao': t['descricao'], 'parametros': t['parametros']} for n, t in permitidas.items()},
        executar,
    )

    destaques, alertas, tabela = [], [], None
    for _, _, resultado in chamadas:
        if not isinstance(resultado, dict) or 'erro' in resultado:
            continue
        destaques.extend(resultado.get('destaques') or [])
        alertas.extend(resultado.get('alertas') or [])
        tabela = resultado.get('tabela') or tabela

    resposta = {
        'intent': '+'.join(dict.fromkeys(nome for nome, _, _ in chamadas)) or 'conversa',
        'texto': texto or 'Não consegui formular uma resposta. Pode reformular a pergunta?',
        'sugestoes': SUGESTOES.get(persona, []),
        'origem': 'backend',
        'persona': persona,
    }
    if destaques:
        resposta['destaques'] = destaques[:6]
    if alertas:
        resposta['alertas'] = alertas[:6]
    if tabela:
        resposta['tabela'] = tabela
    return resposta
