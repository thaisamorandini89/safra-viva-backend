from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas.centro_custo_schema import CentroCustoCreate
from services.centro_custo_service import CentroCustoService, serializar_centro_custo

centro_custo_bp = Blueprint('centro_custo', __name__)


@centro_custo_bp.route('/centros-custo', methods=['POST'])
def criar_centro_custo():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados do centro de custo devem ser fornecidos no formato JSON."}), 400

        try:
            payload = CentroCustoCreate.model_validate(dados)
        except ValidationError as e:
            erros = [
                {"campo": ".".join(str(p) for p in err["loc"]), "mensagem": err["msg"]}
                for err in e.errors()
            ]
            return jsonify({"error": "Dados do centro de custo inválidos.", "details": erros}), 400

        centro = CentroCustoService.criar(payload)
        return jsonify({
            "message": "Centro de custo cadastrado com sucesso!",
            **serializar_centro_custo(centro),
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao cadastrar o centro de custo.", "details": str(e)}), 500


@centro_custo_bp.route('/centros-custo', methods=['GET'])
def listar_centros_custo():
    try:
        centros = CentroCustoService.listar()
        return jsonify(centros), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar os centros de custo.", "details": str(e)}), 500
