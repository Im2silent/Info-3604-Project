from flask import Blueprint, request, jsonify
from App.models.checkin import CheckIn
from datetime import datetime
from App import db

check_bp = Blueprint("checkin", __name__)

@checkin_bp.route("/checkin", methods=["POST"])
def checkin():
    data = request.json

    check = CheckIn(
        user_id=data["user_id"],
        timestamp=datetime.utcnow()
    )

    db.session.add(check)
    db.session.commit()

    return jsonify({"message": "Checked in"})