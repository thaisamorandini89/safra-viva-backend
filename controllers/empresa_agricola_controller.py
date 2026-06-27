from flask import Blueprint, request, jsonify
from services.empresa_agricola_service import EmpresaAgricolaService

empresa_bp = Blueprint('empresa', __name__)

@empresa_bp.route('/empresas-agricolas', methods=['GET'])
def listar_empresas():
    try:
        empresas = EmpresaAgricolaService.listar_todas()
        return jsonify(empresas), 200
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor ao carregar empresas.", "details": str(e)}), 500

@empresa_bp.route('/empresas-agricolas', methods=['POST'])
def criar_empresa():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400
            
        nova_empresa = EmpresaAgricolaService.criar_empresa(dados)
        
        return jsonify({
            "message": "Empresa agrícola cadastrada com sucesso!",
            "id_empresa": nova_empresa.id_empresa,
            "razao_social": nova_empresa.razao_social
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha de processamento das informações.", "details": str(e)}), 500



