from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas.movimentacao_schema import MovimentacaoCreate
from services.movimentacao_service import MovimentacaoService

movimentacao_bp = Blueprint('movimentacao', __name__)


@movimentacao_bp.route('/movimentacoes', methods=['POST'])
def registrar_movimentacao():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados da movimentação devem ser fornecidos no formato JSON."}), 400

        try:
            payload = MovimentacaoCreate.model_validate(dados)
        except ValidationError as e:
            erros = [
                {"campo": ".".join(str(p) for p in err["loc"]), "mensagem": err["msg"]}
                for err in e.errors()
            ]
            return jsonify({"error": "Dados da movimentação inválidos.", "details": erros}), 400

        movimentacao, insumo = MovimentacaoService.registrar(payload)

        return jsonify({
            "message": "Movimentação registrada com sucesso!",
            "id_movimentacao": movimentacao.id_movimentacao,
            "id_insumo": movimentacao.id_insumo,
            "tipo_movimentacao": movimentacao.tipo_movimentacao,
            "quantidade": float(movimentacao.quantidade),
            "id_responsavel": movimentacao.id_responsavel,
            "observacao": movimentacao.observacao,
            "estoque_atual": float(insumo.estoque_atual)
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao registrar a movimentação.", "details": str(e)}), 500


@movimentacao_bp.route('/movimentacoes', methods=['GET'])
def listar_movimentacoes():
    try:
        id_insumo = request.args.get('id_insumo', type=int)
        movimentacoes = MovimentacaoService.listar(id_insumo=id_insumo)
        return jsonify(movimentacoes), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar as movimentações.", "details": str(e)}), 500
