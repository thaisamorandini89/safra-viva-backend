from flask import Blueprint, request, jsonify
from services.tipo_atividade_service import TipoAtividadeService

tipo_atividade_bp = Blueprint('tipo_atividade', __name__)


@tipo_atividade_bp.route('/tipos-atividade', methods=['GET'])
def listar():
    try:
        id_cat = request.args.get('id_categoria_atividade', type=int)
        return jsonify(TipoAtividadeService.listar_todos(id_cat)), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar tipos de atividade.", "details": str(e)}), 500


@tipo_atividade_bp.route('/tipos-atividade', methods=['POST'])
def criar():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados devem ser fornecidos no formato JSON."}), 400
        novo = TipoAtividadeService.criar(dados)
        return jsonify({
            "message": "Tipo de atividade cadastrado com sucesso!",
            "id_atividade": novo.id_atividade,
            "descricao": novo.descricao,
            "id_categoria_atividade": novo.id_categoria_atividade,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao cadastrar o tipo.", "details": str(e)}), 500


@tipo_atividade_bp.route('/tipos-atividade/<int:id_atividade>', methods=['GET'])
def buscar(id_atividade):
    try:
        return jsonify(TipoAtividadeService.buscar_por_id(id_atividade)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar o tipo.", "details": str(e)}), 500


@tipo_atividade_bp.route('/tipos-atividade/<int:id_atividade>', methods=['PUT'])
def atualizar(id_atividade):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados devem ser fornecidos no formato JSON."}), 400
        t = TipoAtividadeService.atualizar(id_atividade, dados)
        return jsonify({
            "message": "Tipo de atividade atualizado com sucesso!",
            "id_atividade": t.id_atividade,
            "descricao": t.descricao,
            "id_categoria_atividade": t.id_categoria_atividade,
        }), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar o tipo.", "details": str(e)}), 500


@tipo_atividade_bp.route('/tipos-atividade/<int:id_atividade>', methods=['DELETE'])
def excluir(id_atividade):
    try:
        TipoAtividadeService.excluir(id_atividade)
        return jsonify({"message": "Tipo de atividade excluído com sucesso!"}), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao excluir o tipo.", "details": str(e)}), 500
