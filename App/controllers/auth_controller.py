from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
from werkzeug.security import gnerate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = reuest.json

    user = User(first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],     

password_hash= generate_password_hash(data["password"]),
role=data["role"]
    ) 
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "User created"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if user and check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Login successful"})
    
    return jsonify({"error": "Invalid credentials"}), 401