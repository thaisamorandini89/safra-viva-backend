from flask import Blueprint, request, jsonify
from services.marca_service import MarcaService

marca_bp = Blueprint('marca', __name__)


@marca_bp.route('/marcas', methods=['GET'])
def listar_marcas():
    try:
        marcas = MarcaService.listar_todos()
        return jsonify([{
            "id_marca": m.id_marca,
            "descricao_marca": m.descricao_marca
        } for m in marcas]), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar as marcas.", "details": str(e)}), 500


@marca_bp.route('/marcas', methods=['POST'])
def criar_marca():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400

        nova_marca = MarcaService.criar_marca(dados)
        return jsonify({
            "message": "Marca cadastrada com sucesso!",
            "id_marca": nova_marca.id_marca,
            "descricao_marca": nova_marca.descricao_marca
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao registrar a marca.", "details": str(e)}), 500


@marca_bp.route('/marcas/<int:id_marca>', methods=['PUT'])
def atualizar_marca(id_marca):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de atualização devem ser fornecidos no formato JSON."}), 400

        marca = MarcaService.atualizar_marca(id_marca, dados)
        return jsonify({
            "message": "Marca atualizada com sucesso!",
            "id_marca": marca.id_marca,
            "descricao_marca": marca.descricao_marca
        }), 200
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar a marca.", "details": str(e)}), 500


@marca_bp.route('/marcas/<int:id_marca>', methods=['DELETE'])
def excluir_marca(id_marca):
    try:
        MarcaService.excluir_marca(id_marca)
        return jsonify({"message": "Marca excluída com sucesso!"}), 200
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao excluir a marca.", "details": str(e)}), 500
