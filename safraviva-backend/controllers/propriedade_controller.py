from flask import Blueprint, jsonify, request
from services.propriedade_service import PropriedadeService

propriedade_bp = Blueprint('propriedade', __name__)
propriedade_service = PropriedadeService()

@propriedade_bp.route('/propriedades', methods=['GET'])
def get_propriedades():
    propriedades = propriedade_service.listar_propriedades()
    return jsonify(propriedades), 200

@propriedade_bp.route('/propriedades', methods=['POST'])
def create_propriedade():
    data = request.get_json()
    nova_propriedade = propriedade_service.criar_propriedade(data)
    return jsonify(nova_propriedade), 201

@propriedade_bp.route('/propriedades/<int:id>', methods=['PUT'])
def update_propriedade(id):
    data = request.get_json()
    propriedade_atualizada = propriedade_service.atualizar_propriedade(id, data)
    return jsonify(propriedade_atualizada), 200

@propriedade_bp.route('/propriedades/<int:id>', methods=['DELETE'])
def delete_propriedade(id):
    propriedade_service.deletar_propriedade(id)
    return jsonify({"message": "Propriedade deletada com sucesso!"}), 204