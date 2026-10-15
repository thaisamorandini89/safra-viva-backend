from flask import Blueprint, request, jsonify
from services.atividade_service import AtividadeService

atividade_bp = Blueprint('atividade', __name__)


@atividade_bp.route('/atividades', methods=['GET'])
def listar_atividades():
    try:
        return jsonify(AtividadeService.listar_todos()), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar as atividades.", "details": str(e)}), 500


@atividade_bp.route('/atividades', methods=['POST'])
def criar_atividade():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400

        nova = AtividadeService.criar_atividade(dados)
        return jsonify({
            "message": "Atividade cadastrada com sucesso!",
            "id_atividade": nova.id_atividade,
            "descricao": nova.descricao,
            "data_atividade": nova.data_atividade.strftime("%Y-%m-%d") if nova.data_atividade else None
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao registrar a atividade.", "details": str(e)}), 500
