from flask import Blueprint, request, jsonify
from services.fornecedor_service import FornecedorService

fornecedor_bp = Blueprint('fornecedor', __name__)


@fornecedor_bp.route('/fornecedores', methods=['GET'])
def listar_fornecedores():
    try:
        return jsonify(FornecedorService.listar_todos()), 200
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor ao carregar fornecedores.", "details": str(e)}), 500


@fornecedor_bp.route('/fornecedores', methods=['POST'])
def criar_fornecedor():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400
        novo = FornecedorService.criar_fornecedor(dados)
        return jsonify({
            "message": "Fornecedor cadastrado com sucesso!",
            "id_fornecedor": novo.id_fornecedor,
            "nome_fornecedor": novo.nome_fornecedor
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha de processamento das informações.", "details": str(e)}), 500


@fornecedor_bp.route('/fornecedores/<int:id_fornecedor>', methods=['GET'])
def buscar_fornecedor(id_fornecedor):
    try:
        return jsonify(FornecedorService.buscar_por_id(id_fornecedor)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar o fornecedor.", "details": str(e)}), 500


@fornecedor_bp.route('/fornecedores/<int:id_fornecedor>', methods=['PUT'])
def atualizar_fornecedor(id_fornecedor):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de atualização devem ser fornecidos no formato JSON."}), 400
        f = FornecedorService.atualizar_fornecedor(id_fornecedor, dados)
        return jsonify({
            "message": "Fornecedor atualizado com sucesso!",
            "id_fornecedor": f.id_fornecedor,
            "nome_fornecedor": f.nome_fornecedor
        }), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar o fornecedor.", "details": str(e)}), 500


@fornecedor_bp.route('/fornecedores/<int:id_fornecedor>', methods=['DELETE'])
def excluir_fornecedor(id_fornecedor):
    try:
        FornecedorService.excluir_fornecedor(id_fornecedor)
        return jsonify({"message": "Fornecedor excluído com sucesso!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao excluir o fornecedor.", "details": str(e)}), 500
