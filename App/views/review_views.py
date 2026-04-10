from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from App.models.review import Review
from App.models.submission import Submission
from App.database import db

review_views = Blueprint('review_views', __name__)

VALID_DECISIONS = {"ACCEPT", "REJECT", "REVISE"}


@review_views.route('/api/reviews', methods=['POST'])
@jwt_required()
def add_review():
    data = request.json or {}
    required = ("submission_id", "reviewer_id", "decision")
    if not all(k in data for k in required):
        return jsonify({"error": f"Missing fields. Required: {list(required)}"}), 400

    if data["decision"] not in VALID_DECISIONS:
        return jsonify({"error": f"decision must be one of {VALID_DECISIONS}"}), 400

    submission = Submission.query.get(data["submission_id"])
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    if submission.author_id == data["reviewer_id"]:
        return jsonify({"error": "Cannot review your own submission"}), 400

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

    status_map = {"ACCEPT": "ACCEPTED", "REJECT": "REJECTED", "REVISE": "REVISION"}
    submission.status = status_map[data["decision"]]

    db.session.commit()
    return jsonify({"message": "Review submitted", "review": review.get_json()}), 201


@review_views.route('/api/reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    submission_id = request.args.get("submission_id")
    reviewer_id = request.args.get("reviewer_id")

    query = Review.query
    if submission_id:
        query = query.filter_by(submission_id=submission_id)
    if reviewer_id:
        query = query.filter_by(reviewer_id=reviewer_id)

    return jsonify([r.get_json() for r in query.all()]), 200


@review_views.route('/api/reviews/<int:review_id>', methods=['GET'])
@jwt_required()
def get_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    return jsonify(review.get_json()), 200
