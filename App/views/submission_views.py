from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from App.models.submission import Submission
from App.models.track import Track
from App.database import db

submission_views = Blueprint('submission_views', __name__)

VALID_TYPES = {"ORAL", "POSTER"}


@submission_views.route('/api/submissions', methods=['POST'])
@jwt_required()
def create_submission():
    data = request.json or {}
    required = ("title", "abstract", "presentation_type", "author_id", "track_id")
    if not all(k in data for k in required):
        return jsonify({"error": f"Missing fields. Required: {list(required)}"}), 400

    if data["presentation_type"] not in VALID_TYPES:
        return jsonify({"error": f"presentation_type must be one of {VALID_TYPES}"}), 400

    if not Track.query.get(data["track_id"]):
        return jsonify({"error": "Track not found"}), 404

    submission = Submission(
        title=data["title"],
        abstract=data["abstract"],
        presentation_type=data["presentation_type"],
        author_id=data["author_id"],
        track_id=data["track_id"]
    )
    db.session.add(submission)
    db.session.commit()
    return jsonify({"message": "Submission created", "submission": submission.get_json()}), 201


@submission_views.route('/api/submissions', methods=['GET'])
@jwt_required()
def get_submissions():
    status = request.args.get("status")
    track_id = request.args.get("track_id")
    ptype = request.args.get("presentation_type")

    query = Submission.query
    if status:
        query = query.filter_by(status=status)
    if track_id:
        query = query.filter_by(track_id=track_id)
    if ptype:
        query = query.filter_by(presentation_type=ptype)

    return jsonify([s.get_json() for s in query.all()]), 200


@submission_views.route('/api/submissions/<int:submission_id>', methods=['GET'])
@jwt_required()
def get_submission(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404
    return jsonify(submission.get_json()), 200


@submission_views.route('/api/submissions/<int:submission_id>', methods=['PUT'])
@jwt_required()
def update_submission(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    data = request.json or {}
    if "title" in data:
        submission.title = data["title"]
    if "abstract" in data:
        submission.abstract = data["abstract"]
    if "presentation_type" in data:
        if data["presentation_type"] not in VALID_TYPES:
            return jsonify({"error": f"presentation_type must be one of {VALID_TYPES}"}), 400
        submission.presentation_type = data["presentation_type"]
    if "status" in data:
        submission.status = data["status"]

    db.session.commit()
    return jsonify({"message": "Submission updated", "submission": submission.get_json()}), 200


@submission_views.route('/api/submissions/<int:submission_id>', methods=['DELETE'])
@jwt_required()
def delete_submission(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404
    db.session.delete(submission)
    db.session.commit()
    return jsonify({"message": "Submission deleted"}), 200
