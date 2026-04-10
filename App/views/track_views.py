from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from App.models.track import Track
from App.database import db

track_views = Blueprint('track_views', __name__)


@track_views.route('/api/tracks', methods=['POST'])
@jwt_required()
def create_track():
    data = request.json or {}
    if "name" not in data:
        return jsonify({"error": "name is required"}), 400

    track = Track(name=data["name"], description=data.get("description"))
    db.session.add(track)
    db.session.commit()
    return jsonify({"message": "Track created", "track": track.get_json()}), 201


@track_views.route('/api/tracks', methods=['GET'])
def get_tracks():
    tracks = Track.query.all()
    return jsonify([t.get_json() for t in tracks]), 200


@track_views.route('/api/tracks/<int:track_id>', methods=['GET'])
def get_track(track_id):
    track = Track.query.get(track_id)
    if not track:
        return jsonify({"error": "Track not found"}), 404
    return jsonify(track.get_json()), 200


@track_views.route('/api/tracks/<int:track_id>', methods=['PUT'])
@jwt_required()
def update_track(track_id):
    track = Track.query.get(track_id)
    if not track:
        return jsonify({"error": "Track not found"}), 404

    data = request.json or {}
    if "name" in data:
        track.name = data["name"]
    if "description" in data:
        track.description = data["description"]

    db.session.commit()
    return jsonify({"message": "Track updated", "track": track.get_json()}), 200


@track_views.route('/api/tracks/<int:track_id>', methods=['DELETE'])
@jwt_required()
def delete_track(track_id):
    track = Track.query.get(track_id)
    if not track:
        return jsonify({"error": "Track not found"}), 404
    db.session.delete(track)
    db.session.commit()
    return jsonify({"message": "Track deleted"}), 200
