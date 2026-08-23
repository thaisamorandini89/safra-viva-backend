from flask import Blueprint, request, jsonify
from services.propriedade_service import PropriedadeService

propriedade_bp = Blueprint('propriedade', __name__)


@propriedade_bp.route('/propriedades', methods=['GET'])
def listar_propriedades():
    try:
        propriedades = PropriedadeService.listar_todas()
        return jsonify(propriedades), 200
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor ao carregar propriedades.", "details": str(e)}), 500


@propriedade_bp.route('/propriedades', methods=['POST'])
def criar_propriedade():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400

        nova_propriedade = PropriedadeService.criar_propriedade(dados)

        return jsonify({
            "message": "Propriedade cadastrada com sucesso!",
            "id_propriedade": nova_propriedade.id_propriedade,
            "nome_propriedade": nova_propriedade.nome_propriedade
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha de processamento das informações.", "details": str(e)}), 500


@propriedade_bp.route('/propriedades/<int:id_propriedade>', methods=['GET'])
def buscar_propriedade(id_propriedade):
    try:
        propriedade = PropriedadeService.buscar_por_id(id_propriedade)
        return jsonify(propriedade), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar a propriedade.", "details": str(e)}), 500


@propriedade_bp.route('/propriedades/<int:id_propriedade>', methods=['PUT'])
def atualizar_propriedade(id_propriedade):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de atualização devem ser fornecidos no formato JSON."}), 400

        propriedade = PropriedadeService.atualizar_propriedade(id_propriedade, dados)

        return jsonify({
            "message": "Propriedade atualizada com sucesso!",
            "id_propriedade": propriedade.id_propriedade,
            "nome_propriedade": propriedade.nome_propriedade
        }), 200
    except ValueError as e:
        status = 404 if "não encontrada" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar a propriedade.", "details": str(e)}), 500


@propriedade_bp.route('/propriedades/<int:id_propriedade>', methods=['DELETE'])
def excluir_propriedade(id_propriedade):
    try:
        PropriedadeService.excluir_propriedade(id_propriedade)
        return jsonify({"message": "Propriedade excluída com sucesso!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao excluir a propriedade.", "details": str(e)}), 500
