from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from schemas.funcionario_schema import (
    FuncionarioCreate,
    FuncionarioUpdate,
    VinculoPropriedadeCreate,
)
from services.funcionario_service import FuncionarioService

funcionario_bp = Blueprint('funcionario', __name__)


def _erros_validacao(e: ValidationError):
    return [
        {"campo": ".".join(str(p) for p in err["loc"]), "mensagem": err["msg"]}
        for err in e.errors()
    ]


@funcionario_bp.route('/funcionarios/indicadores', methods=['GET'])
def indicadores_funcionarios():
    try:
        return jsonify(FuncionarioService.indicadores()), 200
    except Exception as e:
        return jsonify({"error": "Erro ao carregar os indicadores.", "details": str(e)}), 500


@funcionario_bp.route('/funcionarios', methods=['GET'])
def listar_funcionarios():
    try:
        status_param = request.args.get('status')
        status = None
        if status_param is not None:
            status = status_param.strip().lower() in ('1', 'true', 'ativo', 'ativos')

        funcionarios = FuncionarioService.listar(
            nome=request.args.get('nome'),
            cpf=request.args.get('cpf'),
            cargo=request.args.get('cargo'),
            id_propriedade=request.args.get('id_propriedade', type=int),
            status=status,
        )
        return jsonify(funcionarios), 200
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor ao carregar funcionários.", "details": str(e)}), 500


@funcionario_bp.route('/funcionarios', methods=['POST'])
def criar_funcionario():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400

        try:
            payload = FuncionarioCreate.model_validate(dados)
        except ValidationError as e:
            return jsonify({"error": "Dados do funcionário inválidos.", "details": _erros_validacao(e)}), 400

        funcionario = FuncionarioService.criar_funcionario(payload)

        return jsonify({
            "message": "Funcionário cadastrado com sucesso!",
            "id_funcionario": funcionario.id_funcionario,
            "nome_completo": funcionario.nome_completo,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha de processamento das informações.", "details": str(e)}), 500


@funcionario_bp.route('/funcionarios/<id_funcionario>', methods=['GET'])
def buscar_funcionario(id_funcionario):
    try:
        funcionario = FuncionarioService.buscar_por_id(id_funcionario)
        return jsonify(funcionario), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao carregar o funcionário.", "details": str(e)}), 500


@funcionario_bp.route('/funcionarios/<id_funcionario>', methods=['PUT'])
def atualizar_funcionario(id_funcionario):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de atualização devem ser fornecidos no formato JSON."}), 400

        try:
            payload = FuncionarioUpdate.model_validate(dados)
        except ValidationError as e:
            return jsonify({"error": "Dados do funcionário inválidos.", "details": _erros_validacao(e)}), 400

        funcionario = FuncionarioService.atualizar_funcionario(id_funcionario, payload)

        return jsonify({
            "message": "Funcionário atualizado com sucesso!",
            "id_funcionario": funcionario.id_funcionario,
            "nome_completo": funcionario.nome_completo,
        }), 200
    except ValueError as e:
        status = 404 if "não encontrado" in str(e).lower() else 400
        return jsonify({"error": str(e)}), status
    except Exception as e:
        return jsonify({"error": "Falha ao atualizar o funcionário.", "details": str(e)}), 500


@funcionario_bp.route('/funcionarios/<id_funcionario>', methods=['DELETE'])
def inativar_funcionario(id_funcionario):
    try:
        FuncionarioService.inativar_funcionario(id_funcionario)
        return jsonify({"message": "Funcionário inativado com sucesso!"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Falha ao inativar o funcionário.", "details": str(e)}), 500


@funcionario_bp.route('/funcionarios/<id_funcionario>/propriedades', methods=['POST'])
def vincular_propriedade(id_funcionario):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados do vínculo devem ser fornecidos no formato JSON."}), 400

        try:
            payload = VinculoPropriedadeCreate.model_validate(dados)
        except ValidationError as e:
            return jsonify({"error": "Dados do vínculo inválidos.", "details": _erros_validacao(e)}), 400

        vinculo = FuncionarioService.vincular_propriedade(id_funcionario, payload.id_propriedade)

        return jsonify({
            "message": "Propriedade vinculada com sucesso!",
            "id_funcionario_propriedade": vinculo.id_funcionario_propriedade,
            "id_funcionario": vinculo.id_funcionario,
            "id_propriedade": vinculo.id_propriedade,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao vincular a propriedade.", "details": str(e)}), 500


@funcionario_bp.route('/funcionarios/<id_funcionario>/propriedades', methods=['GET'])
def listar_propriedades_funcionario(id_funcionario):
    try:
        propriedades = FuncionarioService.listar_propriedades(id_funcionario)
        return jsonify(propriedades), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro ao listar as propriedades do funcionário.", "details": str(e)}), 500
