from flask import Blueprint, request, jsonify
from services.regime_tributario_service import RegimeTributarioService

regime_bp = Blueprint('regime', __name__)

@regime_bp.route('/regimes-tributarios', methods=['GET'])
def listar_regimes_tributarios():
    try:
        regimes = RegimeTributarioService.listar_todos()
        return jsonify([{"id": r.id, "descricao": r.descricao} for r in regimes]), 200
    except Exception as e:
        return jsonify({"error": "Erro ao listar os regimes tributários.", "details": str(e)}), 500

@regime_bp.route('/regimes-tributarios', methods=['POST'])
def criar_regime_tributario():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"error": "Os dados de cadastro devem ser fornecidos no formato JSON."}), 400
            
        novo_regime = RegimeTributarioService.criar_regime(dados)
        return jsonify({
            "message": "Regime tributário cadastrado com sucesso!",
            "id": novo_regime.id,
            "descricao": novo_regime.descricao
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Falha ao registrar o regime tributário.", "details": str(e)}), 500
