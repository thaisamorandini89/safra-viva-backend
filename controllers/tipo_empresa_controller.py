from flask import Blueprint, request, jsonify
from services.tipo_empresa_service import TipoEmpresaService

tipo_empresa_bp = Blueprint('tipo_empresa', __name__)

@tipo_empresa_bp.route('/tipos-empresa', methods=['GET'])
def listar_tipos_empresa():
    try:
        tipos = TipoEmpresaService.listar_todos()
        return jsonify([{"id": t.id, "descricao": t.descricao} for t in tipos]), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar os tipos de empresa.", "details": str(e)}), 500

@tipo_empresa_bp.route('/tipos-empresa', methods=['POST'])
def criar_tipo_empresa():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400
            
        novo_tipo = TipoEmpresaService.criar_tipo(dados)
        return jsonify({
            "message": "Tipo de empresa cadastrado com sucesso!",
            "id": novo_tipo.id,
            "descricao": novo_tipo.descricao
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao registrar o tipo de empresa.", "details": str(e)}), 500
