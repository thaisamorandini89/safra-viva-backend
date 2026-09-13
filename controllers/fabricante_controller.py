from flask import Blueprint, request, jsonify
from services.fabricante_service import FabricanteService

fabricante_bp = Blueprint('fabricante', __name__)


@fabricante_bp.route('/fabricantes', methods=['GET'])
def listar_fabricantes():
    try:
        return jsonify(FabricanteService.listar_todos()), 200
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor ao carregar fabricantes.", "details": str(e)}), 500


@fabricante_bp.route('/fabricantes', methods=['POST'])
def criar_fabricante():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400
        novo = FabricanteService.criar_fabricante(dados)
        return jsonify({
            "message": "Fabricante cadastrado com sucesso!",
            "id_fabricante": novo.id_fabricante,
            "nome_fabricante": novo.nome_fabricante
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha de processamento das informações.", "details": str(e)}), 500


@fabricante_bp.route('/fabricantes/<int:id_fabricante>', methods=['GET'])
def buscar_fabricante(id_fabricante):
    try:
        return jsonify(FabricanteService.buscar_por_id(id_fabricante)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar o fabricante.", "details": str(e)}), 500


@fabricante_bp.route('/fabricantes/<int:id_fabricante>', methods=['PUT'])
def atualizar_fabricante(id_fabricante):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de atualização devem ser fornecidos no formato JSON."}), 400
        f = FabricanteService.atualizar_fabricante(id_fabricante, dados)
        return jsonify({
            "message": "Fabricante atualizado com sucesso!",
            "id_fabricante": f.id_fabricante,
            "nome_fabricante": f.nome_fabricante
        }), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar o fabricante.", "details": str(e)}), 500


@fabricante_bp.route('/fabricantes/<int:id_fabricante>', methods=['DELETE'])
def excluir_fabricante(id_fabricante):
    try:
        FabricanteService.excluir_fabricante(id_fabricante)
        return jsonify({"message": "Fabricante excluído com sucesso!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao excluir o fabricante.", "details": str(e)}), 500
