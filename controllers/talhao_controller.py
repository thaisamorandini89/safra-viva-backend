from flask import Blueprint, request, jsonify
from services.talhao_service import TalhaoService

talhao_bp = Blueprint('talhao', __name__)


@talhao_bp.route('/talhoes', methods=['GET'])
def listar_talhoes():
    try:
        talhoes = TalhaoService.listar_todos()
        return jsonify(talhoes), 200
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor ao carregar talhões.", "details": str(e)}), 500


@talhao_bp.route('/talhoes', methods=['POST'])
def criar_talhao():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400

        novo_talhao = TalhaoService.criar_talhao(dados)

        return jsonify({
            "message": "Talhão cadastrado com sucesso!",
            "id_talhao": novo_talhao.id_talhao,
            "nome_talhao": novo_talhao.nome_talhao
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha de processamento das informações.", "details": str(e)}), 500


@talhao_bp.route('/propriedades/<int:id_propriedade>/talhoes', methods=['GET'])
def listar_talhoes_por_propriedade(id_propriedade):
    try:
        talhoes = TalhaoService.listar_por_propriedade(id_propriedade)
        return jsonify(talhoes), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar os talhões da propriedade.", "details": str(e)}), 500


@talhao_bp.route('/talhoes/<int:id_talhao>', methods=['GET'])
def buscar_talhao(id_talhao):
    try:
        talhao = TalhaoService.buscar_por_id(id_talhao)
        return jsonify(talhao), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar o talhão.", "details": str(e)}), 500


@talhao_bp.route('/talhoes/<int:id_talhao>', methods=['PUT'])
def atualizar_talhao(id_talhao):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de atualização devem ser fornecidos no formato JSON."}), 400

        talhao = TalhaoService.atualizar_talhao(id_talhao, dados)

        return jsonify({
            "message": "Talhão atualizado com sucesso!",
            "id_talhao": talhao.id_talhao,
            "nome_talhao": talhao.nome_talhao
        }), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar o talhão.", "details": str(e)}), 500


@talhao_bp.route('/talhoes/<int:id_talhao>', methods=['DELETE'])
def excluir_talhao(id_talhao):
    try:
        TalhaoService.excluir_talhao(id_talhao)
        return jsonify({"message": "Talhão excluído com sucesso!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao excluir o talhão.", "details": str(e)}), 500
