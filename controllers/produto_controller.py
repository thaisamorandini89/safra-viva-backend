from flask import Blueprint, request, jsonify
from services.produto_service import ProdutoService

produto_bp = Blueprint('produto', __name__)


@produto_bp.route('/produtos', methods=['GET'])
def listar_produtos():
    try:
        produtos = ProdutoService.listar_todos()
        return jsonify(produtos), 200
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor ao carregar produtos.", "details": str(e)}), 500


@produto_bp.route('/produtos', methods=['POST'])
def criar_produto():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400

        novo_produto = ProdutoService.criar_produto(dados)

        return jsonify({
            "message": "Produto cadastrado com sucesso!",
            "id_produto": novo_produto.id_produto,
            "nome_produto": novo_produto.nome_produto
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha de processamento das informações.", "details": str(e)}), 500


@produto_bp.route('/produtos/<int:id_produto>', methods=['GET'])
def buscar_produto(id_produto):
    try:
        produto = ProdutoService.buscar_por_id(id_produto)
        return jsonify(produto), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar o produto.", "details": str(e)}), 500


@produto_bp.route('/produtos/<int:id_produto>', methods=['PUT'])
def atualizar_produto(id_produto):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de atualização devem ser fornecidos no formato JSON."}), 400

        produto = ProdutoService.atualizar_produto(id_produto, dados)

        return jsonify({
            "message": "Produto atualizado com sucesso!",
            "id_produto": produto.id_produto,
            "nome_produto": produto.nome_produto
        }), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar o produto.", "details": str(e)}), 500


@produto_bp.route('/produtos/<int:id_produto>', methods=['DELETE'])
def excluir_produto(id_produto):
    try:
        ProdutoService.excluir_produto(id_produto)
        return jsonify({"message": "Produto excluído com sucesso!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao excluir o produto.", "details": str(e)}), 500
