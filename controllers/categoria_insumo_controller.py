from flask import Blueprint, request, jsonify
from services.categoria_insumo_service import CategoriaInsumoService

categoria_insumo_bp = Blueprint('categoria_insumo', __name__)


@categoria_insumo_bp.route('/categorias-insumo', methods=['GET'])
def listar_categorias():
    try:
        categorias = CategoriaInsumoService.listar_todas()
        return jsonify(categorias), 200
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor ao carregar categorias de insumo.", "details": str(e)}), 500


@categoria_insumo_bp.route('/categorias-insumo', methods=['POST'])
def criar_categoria():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400

        nova_categoria = CategoriaInsumoService.criar_categoria(dados)

        return jsonify({
            "message": "Categoria de insumo cadastrada com sucesso!",
            "id_categoria_insumo": nova_categoria.id_categoria_insumo,
            "nome_categoria": nova_categoria.nome_categoria
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha de processamento das informações.", "details": str(e)}), 500


@categoria_insumo_bp.route('/categorias-insumo/<int:id_categoria_insumo>', methods=['GET'])
def buscar_categoria(id_categoria_insumo):
    try:
        categoria = CategoriaInsumoService.buscar_por_id(id_categoria_insumo)
        return jsonify(categoria), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar a categoria de insumo.", "details": str(e)}), 500


@categoria_insumo_bp.route('/categorias-insumo/<int:id_categoria_insumo>', methods=['PUT'])
def atualizar_categoria(id_categoria_insumo):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de atualização devem ser fornecidos no formato JSON."}), 400

        categoria = CategoriaInsumoService.atualizar_categoria(id_categoria_insumo, dados)

        return jsonify({
            "message": "Categoria de insumo atualizada com sucesso!",
            "id_categoria_insumo": categoria.id_categoria_insumo,
            "nome_categoria": categoria.nome_categoria
        }), 200
    except ValueError as e:
        status = 404 if "não encontrada" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar a categoria de insumo.", "details": str(e)}), 500


@categoria_insumo_bp.route('/categorias-insumo/<int:id_categoria_insumo>', methods=['DELETE'])
def excluir_categoria(id_categoria_insumo):
    try:
        CategoriaInsumoService.excluir_categoria(id_categoria_insumo)
        return jsonify({"message": "Categoria de insumo excluída com sucesso!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao excluir a categoria de insumo.", "details": str(e)}), 500
