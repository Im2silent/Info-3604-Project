from flask import Blueprint, request, jsonify
from app.models.review import Review
from app.models.submission import Submission
from app import db

review_bp = Blueprint("review", __name__)

@review_bp.route("/review", methods=["POST"])
def add_review():
    data = request.json

    submission = Submission.query.get(data["submission_id"])

    if submission.author_id == data["reviewer_id"]:
        return jsonify({"error": "Cannot review your own submission"}), 400
    
    review = Review(

        submission_id=data["submission_id"],
        reviewer_id=data["reviewer_id"],
        score=data["score"],
        comments=data["comments"],
        decision=data["decision"]
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({"message": "Review added"})