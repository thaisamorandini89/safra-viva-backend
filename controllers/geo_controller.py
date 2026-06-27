from flask import Blueprint, jsonify
from services.geo_service import GeoService

geo_bp = Blueprint('geo', __name__)

@geo_bp.route('/estados', methods=['GET'])
def get_estados():
    estados = GeoService.get_all_estados()
    return jsonify([
        {"id": e.id_estado, "uf": e.uf_estado, "nome": e.nome_estado} 
        for e in estados
    ])

@geo_bp.route('/estados/<int:id_estado>/cidades', methods=['GET'])
def get_cidades(id_estado):
    cidades = GeoService.get_cidades_por_estado(id_estado)
    return jsonify([
        {"id": c.id_cidade, "nome": c.nome_cidade, "id_estado": c.id_estado} 
        for c in cidades
    ])