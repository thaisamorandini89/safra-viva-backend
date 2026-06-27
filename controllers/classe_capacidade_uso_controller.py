from flask import Blueprint, request, jsonify
from services.classe_capacidade_uso_service import ClasseCapacidadeUsoService

classe_uso_bp = Blueprint('classe_uso', __name__)

@classe_uso_bp.route('/classes-uso', methods=['GET'])
def listar_classes_uso():
    try:
        classes = ClasseCapacidadeUsoService.listar_todos()
        return jsonify([{
            "id_classe_capacidade_uso": c.id_classe_capacidade_uso, 
            "sigla": c.sigla,
            "descricao": c.descricao,
            "aptidao_principal": c.aptidao_principal
        } for c in classes]), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar as classes de uso.", "details": str(e)}), 500

@classe_uso_bp.route('/classes-uso', methods=['POST'])
def criar_classe_uso():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados devem ser fornecidos no formato JSON."}), 400
            
        nova_classe = ClasseCapacidadeUsoService.criar_classe(dados)
        return jsonify({
            "message": "Classe de Capacidade de Uso cadastrada com sucesso!",
            "id_classe_capacidade_uso": nova_classe.id_classe_capacidade_uso,
            "sigla": nova_classe.sigla,
            "descricao": nova_classe.descricao,
            "aptidao_principal": nova_classe.aptidao_principal
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao registrar a classe de uso.", "details": str(e)}), 500