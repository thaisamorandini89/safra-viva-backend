from flask import Blueprint, jsonify, request
from services.tipo_solo_service import TipoSoloService

tipo_solo_bp = Blueprint('tipo_solo', __name__)
tipo_solo_service = TipoSoloService()

@tipo_solo_bp.route('/tipo-solo', methods=['GET'])
def get_tipo_solo():
    tipos_solo = tipo_solo_service.get_all()
    return jsonify(tipos_solo), 200

@tipo_solo_bp.route('/tipo-solo', methods=['POST'])
def create_tipo_solo():
    data = request.get_json()
    tipo_solo = tipo_solo_service.create(data)
    return jsonify(tipo_solo), 201

@tipo_solo_bp.route('/tipo-solo/<int:id>', methods=['PUT'])
def update_tipo_solo(id):
    data = request.get_json()
    tipo_solo = tipo_solo_service.update(id, data)
    return jsonify(tipo_solo), 200

@tipo_solo_bp.route('/tipo-solo/<int:id>', methods=['DELETE'])
def delete_tipo_solo(id):
    tipo_solo_service.delete(id)
    return jsonify({"message": "Tipo de solo deletado com sucesso!"}), 204