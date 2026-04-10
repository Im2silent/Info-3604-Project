from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from App.models.user import User
from App.database import db

user_views = Blueprint('user_views', __name__)


@user_views.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    role = request.args.get("role")
    query = User.query
    if role:
        query = query.filter_by(role=role)
    return jsonify([u.get_json() for u in query.all()]), 200


@user_views.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.get_json()), 200


@user_views.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json or {}
    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "bio" in data:
        user.bio = data["bio"]
    if "profile_picture" in data:
        user.profile_picture = data["profile_picture"]

    db.session.commit()
    return jsonify({"message": "User updated", "user": user.get_json()}), 200


@user_views.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200
