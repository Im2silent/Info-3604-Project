from flask import Blueprint, request, jsonify
from App.models.poster_assignment import PosterAssignment
from App.models.poster_board import PosterBoard
from App.models.submission import Submission
from App.database import db

poster_bp = Blueprint("poster", __name__)

@poster_bp.route("/assign-poster", methods=["POST"])
def assign_poster():
    data = request.json

    if not data or not all(k in data for k in ("submission_id", "board_id")):
        return jsonify({"error": "Missing submission_id or board_id"}), 400

    submission = Submission.query.get(data["submission_id"])
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    if submission.presentation_type != "POSTER":
        return jsonify({"error": "Submission is not a poster presentation"}), 400

    board = PosterBoard.query.get(data["board_id"])
    if not board:
        return jsonify({"error": "Poster board not found"}), 404

    # Check if board spot is already taken
    existing = PosterAssignment.query.filter_by(board_id=data["board_id"]).first()
    if existing:
        return jsonify({"error": "Poster board spot already assigned"}), 409

    assignment = PosterAssignment(
        submission_id=data["submission_id"],
        board_id=data["board_id"]
    )

    db.session.add(assignment)
    db.session.commit()

    return jsonify({"message": "Poster assigned successfully", "assignment": assignment.get_json()}), 201

@poster_bp.route("/poster-boards", methods=["GET"])
def get_boards():
    track_id = request.args.get("track_id")
    query = PosterBoard.query
    if track_id:
        query = query.filter_by(track_id=track_id)
    boards = query.all()
    return jsonify([b.get_json() for b in boards]), 200


@poster_bp.route("/poster-boards", methods=["POST"])
def create_board():
    data = request.json

    if not data or not all(k in data for k in ("code", "track_id")):
        return jsonify({"error": "Missing code or track_id"}), 400

    board = PosterBoard(code=data["code"], track_id=data["track_id"])
    db.session.add(board)
    db.session.commit()

    return jsonify({"message": "Board created", "board": board.get_json()}), 201