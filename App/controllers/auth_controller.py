from flask import Blueprint, request, jsonify
from App.models.user import User
from App.database import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data or not all(k in data for k in ("first_name", "last_name", "email", "password", "role")):
        return jsonify({"error": "Missing required fields"}), 400

    existing = User.query.filter_by(email=data["email"]).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        password=data["password"],
        role=data["role"]
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created", "user": user.get_json()}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if user and user.check_password(data["password"]):
        user.logged_in = True
        db.session.commit()
        return jsonify({"message": "Login successful", "user": user.get_json()}), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/logout", methods=["POST"])
def logout():
    data = request.json

    if not data or "user_id" not in data:
        return jsonify({"error": "Missing user_id"}), 400

    user = User.query.get(data["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.logout()
    return jsonify({"message": "Logged out successfully"}), 200
