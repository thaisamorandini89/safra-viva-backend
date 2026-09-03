from flask import Blueprint, jsonify, request
from services.geo_service import GeoService

geo_bp = Blueprint('geo', __name__)
geo_service = GeoService()

@geo_bp.route('/locations', methods=['GET'])
def get_locations():
    locations = geo_service.get_all_locations()
    return jsonify(locations), 200

@geo_bp.route('/locations', methods=['POST'])
def create_location():
    data = request.json
    new_location = geo_service.create_location(data)
    return jsonify(new_location), 201

@geo_bp.route('/locations/<int:location_id>', methods=['GET'])
def get_location(location_id):
    location = geo_service.get_location_by_id(location_id)
    if location:
        return jsonify(location), 200
    return jsonify({"error": "Location not found"}), 404

@geo_bp.route('/locations/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    data = request.json
    updated_location = geo_service.update_location(location_id, data)
    if updated_location:
        return jsonify(updated_location), 200
    return jsonify({"error": "Location not found"}), 404

@geo_bp.route('/locations/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    success = geo_service.delete_location(location_id)
    if success:
        return jsonify({"message": "Location deleted"}), 204
    return jsonify({"error": "Location not found"}), 404