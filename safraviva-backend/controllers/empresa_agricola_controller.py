from flask import Blueprint, jsonify, request
from services.empresa_agricola_service import EmpresaAgricolaService

empresa_bp = Blueprint('empresa', __name__)
service = EmpresaAgricolaService()

@empresa_bp.route('/empresa', methods=['GET'])
def get_empresas():
    empresas = service.get_all_empresas()
    return jsonify(empresas), 200

@empresa_bp.route('/empresa', methods=['POST'])
def create_empresa():
    data = request.get_json()
    new_empresa = service.create_empresa(data)
    return jsonify(new_empresa), 201

@empresa_bp.route('/empresa/<int:empresa_id>', methods=['GET'])
def get_empresa(empresa_id):
    empresa = service.get_empresa_by_id(empresa_id)
    if empresa:
        return jsonify(empresa), 200
    return jsonify({"message": "Empresa not found"}), 404

@empresa_bp.route('/empresa/<int:empresa_id>', methods=['PUT'])
def update_empresa(empresa_id):
    data = request.get_json()
    updated_empresa = service.update_empresa(empresa_id, data)
    if updated_empresa:
        return jsonify(updated_empresa), 200
    return jsonify({"message": "Empresa not found"}), 404

@empresa_bp.route('/empresa/<int:empresa_id>', methods=['DELETE'])
def delete_empresa(empresa_id):
    success = service.delete_empresa(empresa_id)
    if success:
        return jsonify({"message": "Empresa deleted successfully"}), 204
    return jsonify({"message": "Empresa not found"}), 404