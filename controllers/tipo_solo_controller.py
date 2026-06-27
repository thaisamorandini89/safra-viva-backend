from flask import Blueprint, request, jsonify
from services.tipo_solo_service import TipoSoloService

tipo_solo_bp = Blueprint('tipo_solo', __name__)

@tipo_solo_bp.route('/tipos-solo', methods=['GET'])
def listar_tipos_solo():
    try:
        tipos = TipoSoloService.listar_todos()
        # Retornamos todos os campos para o frontend ter flexibilidade
        return jsonify([{
            "id": t.id, 
            "descricao": t.descricao,
            "sigla": t.sigla,
            "classe_textural": t.classe_textural
        } for t in tipos]), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar os tipos de solo.", "details": str(e)}), 500

@tipo_solo_bp.route('/tipos-solo', methods=['POST'])
def criar_tipo_solo():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400
            
        novo_tipo = TipoSoloService.criar_tipo(dados)
        return jsonify({
            "message": "Tipo de solo cadastrado com sucesso!",
            "id": novo_tipo.id,
            "descricao": novo_tipo.descricao,
            "sigla": novo_tipo.sigla,
            "classe_textural": novo_tipo.classe_textural
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao registrar o tipo de solo.", "details": str(e)}), 500