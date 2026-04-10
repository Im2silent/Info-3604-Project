from flask import Blueprint, request, jsonify
from App.models.submission import Submission
from App.database import db

submission_bp = Blueprint("submission", __name__)

VALID_PRESENTATION_TYPES = {"ORAL", "POSTER"}

@submission_bp.route("/submit", methods=["POST"])
def submit_abstract():
    data = request.json

    if not data or not all(k in data for k in ("title", "abstract", "presentation_type", "author_id", "track_id")):
        return jsonify({"error": "Missing required fields"}), 400

    if data["presentation_type"] not in VALID_PRESENTATION_TYPES:
        return jsonify({"error": f"Invalid presentation_type. Must be one of: {VALID_PRESENTATION_TYPES}"}), 400

    submission = Submission(
        title=data["title"],
        abstract=data["abstract"],

        presentation_type=data["presentation_type"],

        author_id=data["author_id"],
        track_id=data["track_id"]
    )

    db.session.add(submission)
    db.session.commit()

    return jsonify({"message": "Submission created successfully", "submission": submission.get_json()}), 201

@submission_bp.route("/submissions", methods=["GET"])
def get_submissions():
    status = request.args.get("status")
    track_id = request.args.get("track_id")
    presentation_type = request.args.get("presentation_type")

    query = Submission.query
    if status:
        query = query.filter_by(status=status)
    if track_id:
        query = query.filter_by(track_id=track_id)
    if presentation_type:
        query = query.filter_by(presentation_type=presentation_type)

    submissions = query.all()
    return jsonify([s.get_json() for s in submissions]), 200


@submission_bp.route("/submissions/<int:submission_id>", methods=["GET"])
def get_submission(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404
    return jsonify(submission.get_json()), 200


@submission_bp.route("/submissions/<int:submission_id>", methods=["PUT"])
def update_submission(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    data = request.json
    if "title" in data:
        submission.title = data["title"]
    if "abstract" in data:
        submission.abstract = data["abstract"]
    if "presentation_type" in data:
        if data["presentation_type"] not in VALID_PRESENTATION_TYPES:
            return jsonify({"error": "Invalid presentation_type"}), 400
        submission.presentation_type = data["presentation_type"]

    db.session.commit()
    return jsonify({"message": "Submission updated", "submission": submission.get_json()}), 200