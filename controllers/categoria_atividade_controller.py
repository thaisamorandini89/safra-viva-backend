from flask import Blueprint, request, jsonify
from services.categoria_atividade_service import CategoriaAtividadeService

categoria_atividade_bp = Blueprint('categoria_atividade', __name__)


@categoria_atividade_bp.route('/categorias-atividade', methods=['GET'])
def listar():
    try:
        return jsonify(CategoriaAtividadeService.listar_todas()), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar categorias de atividade.", "details": str(e)}), 500


@categoria_atividade_bp.route('/categorias-atividade', methods=['POST'])
def criar():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados devem ser fornecidos no formato JSON."}), 400
        nova = CategoriaAtividadeService.criar(dados)
        return jsonify({
            "message": "Categoria de atividade cadastrada com sucesso!",
            "id_categoria_atividade": nova.id_categoria_atividade,
            "nome": nova.nome,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao cadastrar a categoria.", "details": str(e)}), 500


@categoria_atividade_bp.route('/categorias-atividade/<int:id_categoria_atividade>', methods=['PUT'])
def atualizar(id_categoria_atividade):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados devem ser fornecidos no formato JSON."}), 400
        cat = CategoriaAtividadeService.atualizar(id_categoria_atividade, dados)
        return jsonify({
            "message": "Categoria de atividade atualizada com sucesso!",
            "id_categoria_atividade": cat.id_categoria_atividade,
            "nome": cat.nome,
        }), 200
    except ValueError as e:
        status = 404 if "não encontrada" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar a categoria.", "details": str(e)}), 500


@categoria_atividade_bp.route('/categorias-atividade/<int:id_categoria_atividade>', methods=['DELETE'])
def excluir(id_categoria_atividade):
    try:
        CategoriaAtividadeService.excluir(id_categoria_atividade)
        return jsonify({"message": "Categoria de atividade excluída com sucesso!"}), 200
    except ValueError as e:
        status = 404 if "não encontrada" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao excluir a categoria.", "details": str(e)}), 500
