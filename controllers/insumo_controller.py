from flask import Blueprint, request, jsonify
from services.insumo_service import InsumoService

insumo_bp = Blueprint('insumo', __name__)


@insumo_bp.route('/insumos', methods=['GET'])
def listar_insumos():
    try:
        insumos = InsumoService.listar_todos()
        return jsonify(insumos), 200
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor ao carregar insumos.", "details": str(e)}), 500


@insumo_bp.route('/insumos', methods=['POST'])
def criar_insumo():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400

        novo_insumo = InsumoService.criar_insumo(dados)

        return jsonify({
            "message": "Insumo cadastrado com sucesso!",
            "id_insumo": novo_insumo.id_insumo,
            "id_produto": novo_insumo.id_produto
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha de processamento das informações.", "details": str(e)}), 500


@insumo_bp.route('/insumos/<int:id_insumo>', methods=['GET'])
def buscar_insumo(id_insumo):
    try:
        insumo = InsumoService.buscar_por_id(id_insumo)
        return jsonify(insumo), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar o insumo.", "details": str(e)}), 500


@insumo_bp.route('/insumos/<int:id_insumo>', methods=['PUT'])
def atualizar_insumo(id_insumo):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de atualização devem ser fornecidos no formato JSON."}), 400

        insumo = InsumoService.atualizar_insumo(id_insumo, dados)

        return jsonify({
            "message": "Insumo atualizado com sucesso!",
            "id_insumo": insumo.id_insumo,
            "id_produto": insumo.id_produto
        }), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar o insumo.", "details": str(e)}), 500


@insumo_bp.route('/insumos/<int:id_insumo>', methods=['DELETE'])
def excluir_insumo(id_insumo):
    try:
        InsumoService.excluir_insumo(id_insumo)
        return jsonify({"message": "Insumo excluído com sucesso!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao excluir o insumo.", "details": str(e)}), 500
