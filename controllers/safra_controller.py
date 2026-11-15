from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas.safra_schema import SafraCreate, SafraUpdate
from services.safra_service import SafraService, serializar_safra

safra_bp = Blueprint('safra', __name__)


def _dados_invalidos(e):
    erros = [
        {"campo": ".".join(str(p) for p in err["loc"]), "mensagem": err["msg"]}
        for err in e.errors()
    ]
    return jsonify({"error": "Dados da safra inválidos.", "details": erros}), 400


@safra_bp.route('/safras', methods=['POST'])
def criar_safra():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados da safra devem ser fornecidos no formato JSON."}), 400

        try:
            payload = SafraCreate.model_validate(dados)
        except ValidationError as e:
            erros = [
                {"campo": ".".join(str(p) for p in err["loc"]), "mensagem": err["msg"]}
                for err in e.errors()
            ]
            return jsonify({"error": "Dados da safra inválidos.", "details": erros}), 400

        safra = SafraService.criar(payload)
        return jsonify({
            "message": "Safra cadastrada com sucesso!",
            **serializar_safra(safra),
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao cadastrar a safra.", "details": str(e)}), 500


@safra_bp.route('/safras', methods=['GET'])
def listar_safras():
    try:
        id_propriedade = request.args.get('id_propriedade', type=int)
        safras = SafraService.listar(id_propriedade=id_propriedade)
        return jsonify(safras), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar as safras.", "details": str(e)}), 500


@safra_bp.route('/safras/<int:id_safra>', methods=['PUT'])
def atualizar_safra(id_safra):
    try:
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"error": "Os dados da safra devem ser fornecidos no formato JSON."}), 400
        try:
            payload = SafraUpdate.model_validate(dados)
        except ValidationError as e:
            return _dados_invalidos(e)

        safra = SafraService.atualizar(id_safra, payload)
        return jsonify({
            "message": "Safra atualizada com sucesso!",
            **serializar_safra(safra),
        }), 200
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar a safra.", "details": str(e)}), 500


@safra_bp.route('/safras/<int:id_safra>', methods=['DELETE'])
def excluir_safra(id_safra):
    try:
        SafraService.excluir(id_safra)
        return jsonify({"message": "Safra excluída com sucesso!"}), 200
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao excluir a safra.", "details": str(e)}), 500
