from flask import Blueprint, request, jsonify
from app.models.schedule import Schedule
from app import db

schedule_bp = Blueprint("schedule", __name__)

@schdeule_bp.route("/schedule", methods=["POST"])
def create_schedule():
    data = request.json

    schedule = Schedule(

        submission_id=data["submission_id"],
        room=data["room"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        track_id=data["track_id"]
    )

    db.session.add(schedule)
    db.session.commit()

    return jsonify({"message": "Schedule successfully"})