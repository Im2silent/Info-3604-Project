from flask import Blueprint, request, jsonify
from App.models.schedule import Schedule
from App.models.staff_assignment import StaffAssignment
from App.models.submission import Submission
from App.database import db
from datetime import datetime

schedule_bp = Blueprint("schedule", __name__)

@schedule_bp.route("/schedule", methods=["POST"])
def create_schedule():
    data = request.json

    if not data or not all(k in data for k in ("submission_id", "room", "start_time", "end_time", "track_id")):
        return jsonify({"error": "Missing required fields"}), 400

    submission = Submission.query.get(data["submission_id"])
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    if submission.status != "ACCEPTED":
        return jsonify({"error": "Only accepted submissions can be scheduled"}), 400

    # Check for existing schedule for this submission
    existing = Schedule.query.filter_by(submission_id=data["submission_id"]).first()
    if existing:
        return jsonify({"error": "Submission is already scheduled"}), 409

    try:
        start_time = datetime.fromisoformat(data["start_time"])
        end_time = datetime.fromisoformat(data["end_time"])
    except ValueError:
        return jsonify({"error": "Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}), 400

    if end_time <= start_time:
        return jsonify({"error": "end_time must be after start_time"}), 400

    schedule = Schedule(

        submission_id=data["submission_id"],
        room=data["room"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        track_id=data["track_id"]
    )

    db.session.add(schedule)
    db.session.commit()

    return jsonify({"message": "Schedule created successfully", "schedule": schedule.get_json()}), 201

@schedule_bp.route("/schedule/<int:schedule_id>/staff", methods=["POST"])
def assign_staff(schedule_id):
    data = request.json

    if not data or not all(k in data for k in ("staff_id", "role")):
        return jsonify({"error": "Missing staff_id or role"}), 400

    VALID_ROLES = {"USHER", "TECH"}
    if data["role"] not in VALID_ROLES:
        return jsonify({"error": f"Invalid role. Must be one of: {VALID_ROLES}"}), 400

    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404

    assignment = StaffAssignment(
        schedule_id=schedule_id,
        staff_id=data["staff_id"],
        role=data["role"]
    )

    db.session.add(assignment)
    db.session.commit()

    return jsonify({"message": "Staff assigned successfully", "assignment": assignment.get_json()}), 201


@schedule_bp.route("/schedules", methods=["GET"])
def get_schedules():
    track_id = request.args.get("track_id")
    query = Schedule.query
    if track_id:
        query = query.filter_by(track_id=track_id)
    schedules = query.all()
    return jsonify([s.get_json() for s in schedules]), 200