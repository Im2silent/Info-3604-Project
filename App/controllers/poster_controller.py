from flask import Blueprint, request, jsonify
from app.models.poster_assignment import PosterAssignment
from app import db

poster_bp = Blueprint("poster", __name__)

@poster_bp.route("/assign-poster", methods=["POST"])
def assign_poster():
    data = request.json

    assignment = PosterAssignment(
        submission_id=data["submission_id"],
        board_id=data["board_id"]
    )

    db.session.add(assignment)
    db.session.commit()

    return jsonify({"message": "Poster assigned"})