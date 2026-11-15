from flask import Blueprint, request, jsonify
from services.maquina_service import MaquinaService

maquina_bp = Blueprint('maquina', __name__)


@maquina_bp.route('/maquinas', methods=['GET'])
def listar():
    try:
        return jsonify(MaquinaService.listar_todas()), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar máquinas.", "details": str(e)}), 500


@maquina_bp.route('/maquinas', methods=['POST'])
def criar():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados devem ser fornecidos no formato JSON."}), 400
        nova = MaquinaService.criar(dados)
        return jsonify({
            "message": "Máquina cadastrada com sucesso!",
            "id_maquina": nova.id_maquina,
            "nome": nova.nome,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao cadastrar a máquina.", "details": str(e)}), 500


@maquina_bp.route('/maquinas/<int:id_maquina>', methods=['GET'])
def buscar(id_maquina):
    try:
        return jsonify(MaquinaService.buscar_por_id(id_maquina)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar a máquina.", "details": str(e)}), 500


@maquina_bp.route('/maquinas/<int:id_maquina>', methods=['PUT'])
def atualizar(id_maquina):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados devem ser fornecidos no formato JSON."}), 400
        m = MaquinaService.atualizar(id_maquina, dados)
        return jsonify({
            "message": "Máquina atualizada com sucesso!",
            "id_maquina": m.id_maquina,
            "nome": m.nome,
        }), 200
    except ValueError as e:
        status = 404 if "não encontrada" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar a máquina.", "details": str(e)}), 500


@maquina_bp.route('/maquinas/<int:id_maquina>', methods=['DELETE'])
def excluir(id_maquina):
    try:
        MaquinaService.excluir(id_maquina)
        return jsonify({"message": "Máquina excluída com sucesso!"}), 200
    except ValueError as e:
        status = 404 if "não encontrada" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao excluir a máquina.", "details": str(e)}), 500
