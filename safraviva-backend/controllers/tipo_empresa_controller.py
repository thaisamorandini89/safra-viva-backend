from flask import Blueprint, jsonify, request
from services.tipo_empresa_service import TipoEmpresaService

tipo_empresa_bp = Blueprint('tipo_empresa', __name__)
tipo_empresa_service = TipoEmpresaService()

@tipo_empresa_bp.route('/tipo_empresa', methods=['GET'])
def get_tipo_empresas():
    tipo_empresas = tipo_empresa_service.get_all()
    return jsonify(tipo_empresas), 200

@tipo_empresa_bp.route('/tipo_empresa/<int:id>', methods=['GET'])
def get_tipo_empresa(id):
    tipo_empresa = tipo_empresa_service.get_by_id(id)
    if tipo_empresa:
        return jsonify(tipo_empresa), 200
    return jsonify({"message": "Tipo de empresa não encontrado"}), 404

@tipo_empresa_bp.route('/tipo_empresa', methods=['POST'])
def create_tipo_empresa():
    data = request.json
    tipo_empresa = tipo_empresa_service.create(data)
    return jsonify(tipo_empresa), 201

@tipo_empresa_bp.route('/tipo_empresa/<int:id>', methods=['PUT'])
def update_tipo_empresa(id):
    data = request.json
    tipo_empresa = tipo_empresa_service.update(id, data)
    if tipo_empresa:
        return jsonify(tipo_empresa), 200
    return jsonify({"message": "Tipo de empresa não encontrado"}), 404

@tipo_empresa_bp.route('/tipo_empresa/<int:id>', methods=['DELETE'])
def delete_tipo_empresa(id):
    success = tipo_empresa_service.delete(id)
    if success:
        return jsonify({"message": "Tipo de empresa deletado com sucesso"}), 204
    return jsonify({"message": "Tipo de empresa não encontrado"}), 404