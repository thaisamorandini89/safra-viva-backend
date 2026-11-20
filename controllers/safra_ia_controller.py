import time
from collections import defaultdict, deque

from flask import Blueprint, current_app, g, jsonify, request
from pydantic import BaseModel, ValidationError, constr

from services.safra_ia import agente
from services.safra_ia.gemini_client import ErroLLM
from services.safra_ia import tools as tools_mod
from services.safra_ia.permissoes import PAPEIS, papel_do_perfil
from utils.auth import requer_auth

safra_ia_bp = Blueprint('safra_ia', __name__)

_chamadas_por_usuario = defaultdict(deque)


class ConsultaSchema(BaseModel):
    pergunta: constr(strip_whitespace=True, min_length=1, max_length=1000)


def _excedeu_limite(id_usuario):
    limite = int(current_app.config.get('SAFRAIA_LIMITE_MINUTO', 20))
    agora = time.monotonic()
    janela = _chamadas_por_usuario[id_usuario]
    while janela and agora - janela[0] > 60:
        janela.popleft()
    if len(janela) >= limite:
        return True
    janela.append(agora)
    return False


@safra_ia_bp.route('/safra-ia/perfil', methods=['GET'])
@requer_auth
def perfil():
    papel = papel_do_perfil(g.usuario.perfil)
    dados = PAPEIS[papel]
    return jsonify({
        'papel': papel,
        'nome_papel': dados['nome'],
        'foco': dados['foco'],
        'saudacao': dados['saudacao'],
        'sugestoes': dados['sugestoes'],
        'consultas': [
            {'nome': nome, 'descricao': tool['descricao']}
            for nome, tool in tools_mod.tools_permitidas(papel).items()
        ],
    }), 200


@safra_ia_bp.route('/safra-ia/consultar', methods=['POST'])
@requer_auth
def consultar():
    try:
        dados = ConsultaSchema(**(request.get_json(silent=True) or {}))
    except ValidationError:
        return jsonify({"error": "Informe uma pergunta (até 1000 caracteres)."}), 422

    if _excedeu_limite(g.usuario.id_usuario):
        return jsonify({"error": "Muitas perguntas em sequência. Aguarde um minuto."}), 429

    try:
        return jsonify(agente.consultar(g.usuario, dados.pergunta)), 200
    except ErroLLM as exc:
        return jsonify({"error": str(exc)}), exc.status
