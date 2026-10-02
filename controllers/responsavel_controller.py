from flask import Blueprint, request, jsonify
from services.responsavel_service import ResponsavelService

responsavel_bp = Blueprint('responsavel', __name__)


@responsavel_bp.route('/responsaveis', methods=['GET'])
def listar_responsaveis():
    try:
        responsaveis = ResponsavelService.listar_todos()
        return jsonify([{
            "id_responsavel": r.id_responsavel,
            "nome": r.nome,
            "cargo": r.cargo,
            "status": r.status
        } for r in responsaveis]), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar os responsáveis.", "details": str(e)}), 500


@responsavel_bp.route('/responsaveis', methods=['POST'])
def criar_responsavel():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400

        novo = ResponsavelService.criar_responsavel(dados)
        return jsonify({
            "message": "Responsável cadastrado com sucesso!",
            "id_responsavel": novo.id_responsavel,
            "nome": novo.nome,
            "cargo": novo.cargo
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao registrar o responsável.", "details": str(e)}), 500
