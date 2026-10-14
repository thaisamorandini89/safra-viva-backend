from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas.lancamento_schema import LancamentoCreate
from services.lancamento_service import LancamentoService, serializar_lancamento

lancamento_bp = Blueprint('lancamento', __name__)


def _validar_payload(dados):
    """Valida o corpo com o schema; retorna (payload, None) ou (None, resposta_erro)."""
    if not dados:
        return None, (jsonify({"error": "Os dados do lançamento devem ser fornecidos no formato JSON."}), 400)
    try:
        return LancamentoCreate.model_validate(dados), None
    except ValidationError as e:
        erros = [
            {"campo": ".".join(str(p) for p in err["loc"]), "mensagem": err["msg"]}
            for err in e.errors()
        ]
        return None, (jsonify({"error": "Dados do lançamento inválidos.", "details": erros}), 400)


@lancamento_bp.route('/lancamentos', methods=['POST'])
def criar_lancamento():
    try:
        payload, erro = _validar_payload(request.get_json())
        if erro:
            return erro
        lancamento = LancamentoService.criar(payload)
        return jsonify({
            "message": "Lançamento cadastrado com sucesso!",
            **serializar_lancamento(lancamento),
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao cadastrar o lançamento.", "details": str(e)}), 500


@lancamento_bp.route('/lancamentos', methods=['GET'])
def listar_lancamentos():
    try:
        filtros = {
            "data_inicio": request.args.get('data_inicio'),
            "data_fim": request.args.get('data_fim'),
            "tipo": request.args.get('tipo'),
            "id_safra": request.args.get('id_safra', type=int),
            "id_propriedade": request.args.get('id_propriedade', type=int),
            "id_talhao": request.args.get('id_talhao', type=int),
        }
        if filtros.get("tipo"):
            filtros["tipo"] = filtros["tipo"].strip().upper()
        lancamentos = LancamentoService.listar(filtros)
        return jsonify(lancamentos), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar os lançamentos.", "details": str(e)}), 500


@lancamento_bp.route('/lancamentos/<id_lancamento>', methods=['PUT'])
def atualizar_lancamento(id_lancamento):
    try:
        payload, erro = _validar_payload(request.get_json())
        if erro:
            return erro
        lancamento = LancamentoService.atualizar(id_lancamento, payload)
        return jsonify({
            "message": "Lançamento atualizado com sucesso!",
            **serializar_lancamento(lancamento),
        }), 200
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar o lançamento.", "details": str(e)}), 500


@lancamento_bp.route('/lancamentos/<id_lancamento>', methods=['DELETE'])
def excluir_lancamento(id_lancamento):
    try:
        LancamentoService.excluir(id_lancamento)
        return jsonify({"message": "Lançamento excluído com sucesso!"}), 200
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao excluir o lançamento.", "details": str(e)}), 500
