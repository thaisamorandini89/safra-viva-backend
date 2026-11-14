from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from services.atividade_agricola_service import AtividadeAgricolaService
from schemas.atividade_schema import AtividadeCreate, AtividadeUpdate, STATUS_ATIVIDADE

atividade_agricola_bp = Blueprint('atividade_agricola', __name__)


def _erros_pydantic(exc):
    return [
        {"campo": ".".join(str(p) for p in e["loc"]), "erro": e["msg"]}
        for e in exc.errors()
    ]


@atividade_agricola_bp.route('/atividades/status-opcoes', methods=['GET'])
def status_opcoes():
    return jsonify(list(STATUS_ATIVIDADE)), 200


@atividade_agricola_bp.route('/atividades/indicadores', methods=['GET'])
def indicadores():
    try:
        filtros = {
            "status": request.args.get("status"),
            "id_categoria_atividade": request.args.get("id_categoria_atividade", type=int),
            "id_tipo_atividade": request.args.get("id_tipo_atividade", type=int),
            "id_talhao": request.args.get("id_talhao", type=int),
            "safra": request.args.get("safra"),
            "busca": request.args.get("busca"),
        }
        return jsonify(AtividadeAgricolaService.indicadores(filtros)), 200
    except Exception as e:
        return jsonify({"error": "Erro ao calcular indicadores.", "details": str(e)}), 500


@atividade_agricola_bp.route('/atividades', methods=['GET'])
def listar():
    try:
        filtros = {
            "status": request.args.get("status"),
            "id_categoria_atividade": request.args.get("id_categoria_atividade", type=int),
            "id_tipo_atividade": request.args.get("id_tipo_atividade", type=int),
            "id_talhao": request.args.get("id_talhao", type=int),
            "safra": request.args.get("safra"),
            "busca": request.args.get("busca"),
        }
        return jsonify(AtividadeAgricolaService.listar(filtros)), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar atividades.", "details": str(e)}), 500


@atividade_agricola_bp.route('/atividades/<int:id_atividade_agricola>', methods=['GET'])
def obter(id_atividade_agricola):
    try:
        return jsonify(AtividadeAgricolaService.obter(id_atividade_agricola)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar a atividade.", "details": str(e)}), 500


@atividade_agricola_bp.route('/atividades', methods=['POST'])
def criar():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados devem ser fornecidos no formato JSON."}), 400
        payload = AtividadeCreate(**dados).model_dump()
        nova = AtividadeAgricolaService.criar(payload)
        return jsonify(nova), 201
    except ValidationError as e:
        return jsonify({"error": "Dados inválidos.", "detalhes": _erros_pydantic(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao cadastrar a atividade.", "details": str(e)}), 500


@atividade_agricola_bp.route('/atividades/<int:id_atividade_agricola>', methods=['PUT'])
def atualizar(id_atividade_agricola):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados devem ser fornecidos no formato JSON."}), 400
        payload = AtividadeUpdate(**dados).model_dump(exclude_unset=True)
        atualizada = AtividadeAgricolaService.atualizar(id_atividade_agricola, payload)
        return jsonify(atualizada), 200
    except ValidationError as e:
        return jsonify({"error": "Dados inválidos.", "detalhes": _erros_pydantic(e)}), 400
    except ValueError as e:
        status = 404 if "não encontrada" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar a atividade.", "details": str(e)}), 500


@atividade_agricola_bp.route('/atividades/<int:id_atividade_agricola>', methods=['DELETE'])
def excluir(id_atividade_agricola):
    try:
        AtividadeAgricolaService.excluir(id_atividade_agricola)
        return jsonify({"message": "Atividade excluída com sucesso!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao excluir a atividade.", "details": str(e)}), 500
