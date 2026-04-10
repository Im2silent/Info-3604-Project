from flask import Blueprint, request, jsonify
from App.models.review import Review
from App.models.submission import Submission
from App.database import db

review_bp = Blueprint("review", __name__)

VALID_DECISIONS = {"ACCEPT", "REJECT", "REVISE"}

@review_bp.route("/review", methods=["POST"])
def add_review():
    data = request.json

    if not data or not all(k in data for k in ("submission_id", "reviewer_id", "decision")):
        return jsonify({"error": "Missing required fields"}), 400

    if data["decision"] not in VALID_DECISIONS:
        return jsonify({"error": f"Invalid decision. Must be one of: {VALID_DECISIONS}"}), 400

    submission = Submission.query.get(data["submission_id"])
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    if submission.author_id == data["reviewer_id"]:
        return jsonify({"error": "Cannot review your own submission"}), 400
    
    # Check reviewer hasn't already reviewed this submission
    existing = Review.query.filter_by(
        submission_id=data["submission_id"],
        reviewer_id=data["reviewer_id"]
    ).first()
    if existing:
        return jsonify({"error": "You have already reviewed this submission"}), 409

    review = Review(

        submission_id=data["submission_id"],
        reviewer_id=data["reviewer_id"],
        score=data.get("score"),
        comments=data.get("comments"),
        decision=data["decision"]
    )

    db.session.add(review)
    
    if data["decision"] == "ACCEPT":
        submission.status = "ACCEPTED"
    elif data["decision"] == "REJECT":
        submission.status = "REJECTED"
    elif data["decision"] == "REVISE":
        submission.status = "REVISION"

    db.session.commit()

    return jsonify({"message": "Review added successfully", "review": review.get_json()}), 201

@review_bp.route("/reviews/<int:submission_id>", methods=["GET"])
def get_reviews(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    reviews = Review.query.filter_by(submission_id=submission_id).all()
    return jsonify([r.get_json() for r in reviews]), 200