from flask import Blueprint, request, jsonify
from App.models.checkin import CheckIn
from App.models.user import User
from datetime import datetime
from App.database import db

checkin_bp = Blueprint("checkin", __name__)

@checkin_bp.route("/checkin", methods=["POST"])
def checkin():
    data = request.json

    if not data or "user_id" not in data:
        return jsonify({"error": "Missing user_id"}), 400

    user = User.query.get(data["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    check = CheckIn(
        user_id=data["user_id"],
        timestamp=datetime.utcnow()
    )

    db.session.add(check)
    db.session.commit()

    return jsonify({"message": "Checked in successfully", "checkin": check.get_json()}), 201

@checkin_bp.route("/checkins", methods=["GET"])
def get_checkins():
    checkins = CheckIn.query.all()
    return jsonify([c.get_json() for c in checkins]), 200