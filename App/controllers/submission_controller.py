from flask import Blueprint, request, jsonify
from app.models.submission import Submission
from app import db

submission_bp = Blueprint("submission", __name__)

@submission_bp.route("/submit", methods=["POST"])
def submit_abstract():
    data = request.json

    submission = Submission(
        title=data["title"],
        abstract=data["abstract"],

        presentation_type=data["presentation_type"],

        author_id=data["author_id"],
        track_id=data["track_id"]
    )

    db.session.add(submission)
    db.session.commit()

    return jsonify({"message": "Submission created"})

@submssion_bp.route("/submissions", methods=["GET"])
def get_submissions():
    submissions = Submission.query.all()

    return jsonify([s.title for s in submissions])