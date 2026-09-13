from flask import Blueprint, jsonify, request
from services.classe_capacidade_uso_service import ClasseCapacidadeUsoService

classe_uso_bp = Blueprint('classe_uso', __name__)
service = ClasseCapacidadeUsoService()

@classe_uso_bp.route('/classe_capacidade_uso', methods=['GET'])
def get_classes():
    classes = service.get_all_classes()
    return jsonify(classes), 200

@classe_uso_bp.route('/classe_capacidade_uso', methods=['POST'])
def create_class():
    data = request.get_json()
    new_class = service.create_class(data)
    return jsonify(new_class), 201

@classe_uso_bp.route('/classe_capacidade_uso/<int:id>', methods=['PUT'])
def update_class(id):
    data = request.get_json()
    updated_class = service.update_class(id, data)
    return jsonify(updated_class), 200

@classe_uso_bp.route('/classe_capacidade_uso/<int:id>', methods=['DELETE'])
def delete_class(id):
    service.delete_class(id)
    return jsonify({"message": "Class deleted successfully"}), 204