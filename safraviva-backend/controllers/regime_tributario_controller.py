from flask import Blueprint, jsonify, request
from services.regime_tributario_service import RegimeTributarioService

regime_bp = Blueprint('regime_bp', __name__)
service = RegimeTributarioService()

@regime_bp.route('/regimes', methods=['GET'])
def get_regimes():
    regimes = service.get_all_regimes()
    return jsonify(regimes), 200

@regime_bp.route('/regimes', methods=['POST'])
def create_regime():
    data = request.json
    new_regime = service.create_regime(data)
    return jsonify(new_regime), 201

@regime_bp.route('/regimes/<int:id>', methods=['PUT'])
def update_regime(id):
    data = request.json
    updated_regime = service.update_regime(id, data)
    return jsonify(updated_regime), 200

@regime_bp.route('/regimes/<int:id>', methods=['DELETE'])
def delete_regime(id):
    service.delete_regime(id)
    return jsonify({"message": "Regime deleted successfully"}), 204