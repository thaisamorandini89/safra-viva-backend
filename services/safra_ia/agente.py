import datetime

from flask import current_app

from services.safra_ia import tools as tools_mod
from services.safra_ia.gemini_client import ClienteGemini
from services.safra_ia.permissoes import PAPEIS, modulos_do_papel, papel_do_perfil


def _sistema(usuario, papel):
    hoje = datetime.date.today().isoformat()
    contexto_papel = PAPEIS[papel]
    modulos = modulos_do_papel(papel)
    sem_acesso = {'Propriedades', 'Talhões', 'Funcionários', 'Atividades', 'Financeiro', 'Insumos'} - modulos
    restricao = (
        f' Este papel não visualiza os módulos: {", ".join(sorted(sem_acesso))}. '
        'Não consulte nem divulgue dados desses módulos; explique qual área do sistema permite acessá-los.'
        if sem_acesso else ''
    )
    if papel == 'colaborador':
        restricao += ' Nenhuma consulta a dados da fazenda está disponível para este papel.'
    return (
        'Você é o SafraIA, assistente do sistema de gestão rural SafraViva. Responda em português do Brasil, '
        'de forma objetiva (até 5 frases), em texto simples sem markdown (sem asteriscos ou #), para o usuário '
        f'{usuario.nome}. Você está falando com {contexto_papel["nome"]} da fazenda, responsável por '
        f'{contexto_papel["foco"]}. Adote um tom {contexto_papel["tom"]}. '
        f'O perfil de login é {papel}. Hoje é {hoje}. '
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
    papel = papel_do_perfil(usuario.perfil)
    contexto_papel = PAPEIS[papel]
    permitidas = tools_mod.tools_permitidas(papel)

    def executar(nome, args):
        resultado = tools_mod.executar_tool(nome, args, usuario.id_empresa, papel)
        return resultado

    cliente = _criar_cliente()
    texto, chamadas = cliente.conversar(
        _sistema(usuario, papel),
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
        'sugestoes': contexto_papel['sugestoes'],
        'origem': 'backend',
        'papel': papel,
    }
    if destaques:
        resposta['destaques'] = destaques[:6]
    if alertas:
        resposta['alertas'] = alertas[:6]
    if tabela:
        resposta['tabela'] = tabela
    return resposta
