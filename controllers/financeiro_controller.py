from flask import Blueprint, request, jsonify

from services.financeiro_service import FinanceiroService

financeiro_bp = Blueprint('financeiro', __name__)


def _filtros_saldo():
    return {
        "data_inicio": request.args.get('data_inicio'),
        "data_fim": request.args.get('data_fim'),
        "id_propriedade": request.args.get('id_propriedade', type=int),
        "id_safra": request.args.get('id_safra', type=int),
    }


@financeiro_bp.route('/financeiro/saldo', methods=['GET'])
def saldo():
    try:
        return jsonify(FinanceiroService.saldo(_filtros_saldo())), 200
    except Exception as e:
        return jsonify({"error": "Erro ao calcular o saldo.", "details": str(e)}), 500


@financeiro_bp.route('/financeiro/fluxo-caixa', methods=['GET'])
def fluxo_caixa():
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        return jsonify(FinanceiroService.fluxo_caixa(data_inicio, data_fim)), 200
    except Exception as e:
        return jsonify({"error": "Erro ao gerar o fluxo de caixa.", "details": str(e)}), 500


@financeiro_bp.route('/financeiro/indicadores', methods=['GET'])
def indicadores():
    try:
        agrupar_por = (request.args.get('agrupar_por') or 'safra').strip().lower()
        return jsonify(FinanceiroService.indicadores(agrupar_por)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro ao calcular os indicadores.", "details": str(e)}), 500
