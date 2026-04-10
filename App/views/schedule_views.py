from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from App.models.schedule import Schedule
from App.models.staff_assignment import StaffAssignment
from App.models.submission import Submission
from App.models.track import Track
from App.models.user import User
from App.database import db
from datetime import datetime
import json

schedule_views = Blueprint('schedule_views', __name__)

ROOMS = ["JFK Auditorium", "Lecture Room A", "Lecture Room B", "Conference Hall", "Seminar Room 1"]
DAY1 = datetime(2025, 11, 26)
DAY2 = datetime(2025, 11, 27)


def _overlapping_sessions(start, end, exclude_id=None):
    """Return all Schedule rows whose time window overlaps [start, end)."""
    q = Schedule.query.filter(
        Schedule.start_time < end,
        Schedule.end_time > start
    )
    if exclude_id:
        q = q.filter(Schedule.id != exclude_id)
    return q.all()


def _check_room_conflict(room, start, end, exclude_id=None):
    """Return the first conflicting session in the same room, or None."""
    for s in _overlapping_sessions(start, end, exclude_id):
        if s.room == room:
            return s
    return None


def _check_staff_conflict(staff_id, start, end, exclude_id=None):
    """Return the first session where this staff member is already assigned
    during the given window, or None."""
    for s in _overlapping_sessions(start, end, exclude_id):
        if any(sa.staff_id == staff_id for sa in s.staff_assignments):
            return s
    return None


def _get_common():
    return {
        'all_tracks': Track.query.all(),
        'tech_staff': User.query.filter_by(role='TECH').all(),
        'ushers': User.query.filter_by(role='USHER').all(),
        'rooms': ROOMS,
    }


def _build_schedule_json(schedules):
    """Build a JS-safe dict of schedule data for the configure modal."""
    data = {}
    for s in schedules:
        tech = next((sa for sa in s.staff_assignments if sa.role == 'TECH'), None)
        usher = next((sa for sa in s.staff_assignments if sa.role == 'USHER'), None)
        data[s.id] = {
            'start_time': s.start_time.strftime('%H:%M'),
            'end_time': s.end_time.strftime('%H:%M'),
            'room': s.room,
            'track_id': s.track_id,
            'tech_staff_id': tech.staff_id if tech else None,
            'usher_id': usher.staff_id if usher else None,
        }
    return json.dumps(data)


# ── HTML page ───────────────────────────────────────────────────

@schedule_views.route('/schedule', methods=['GET'])
def schedule_page():
    active_day = int(request.args.get('day', 1))
    track_id = request.args.get('track_id')

    all_schedules = Schedule.query.order_by(Schedule.start_time).all()

    def filter_day(day_dt):
        q = [s for s in all_schedules if s.start_time.date() == day_dt.date()]
        if track_id:
            q = [s for s in q if str(s.track_id) == str(track_id)]
        return q

    day1 = filter_day(DAY1)
    day2 = filter_day(DAY2)
    all_for_json = day1 + day2

    unscheduled = Submission.query.filter_by(
        presentation_type='ORAL', status='ACCEPTED'
    ).filter(~Submission.id.in_(
        [s.submission_id for s in all_schedules]
    )).all()

    return render_template('schedule.html',
        active_page='schedule',
        active_day=active_day,
        day1_schedules=day1,
        day2_schedules=day2,
        unscheduled_oral=unscheduled,
        schedule_data_json=_build_schedule_json(all_for_json),
        **_get_common()
    )


# ── Add session (form POST) ──────────────────────────────────────

@schedule_views.route('/schedule/add', methods=['POST'])
def add_schedule():
    data = request.form
    day = int(data.get('day', 1))
    base = DAY1 if day == 1 else DAY2

    try:
        start_h, start_m = map(int, data['start_time'].split(':'))
        end_h, end_m = map(int, data['end_time'].split(':'))
        start_time = base.replace(hour=start_h, minute=start_m)
        end_time = base.replace(hour=end_h, minute=end_m)
    except Exception:
        flash('Invalid time format', 'error')
        return redirect(url_for('schedule_views.schedule_page', day=day))

    if end_time <= start_time:
        flash('End time must be after start time', 'error')
        return redirect(url_for('schedule_views.schedule_page', day=day))

    sub_id = data.get('submission_id')
    if not sub_id:
        flash('Select a submission', 'error')
        return redirect(url_for('schedule_views.schedule_page', day=day))

    # ── Conflict checks ──────────────────────────────────────────
    room_conflict = _check_room_conflict(data['room'], start_time, end_time)
    if room_conflict:
        flash(
            f'Room conflict: {data["room"]} is already booked '
            f'{room_conflict.start_time.strftime("%H:%M")}–{room_conflict.end_time.strftime("%H:%M")} '
            f'for "{room_conflict.submission.title}".',
            'error'
        )
        return redirect(url_for('schedule_views.schedule_page', day=day))

    tech_id = data.get('tech_staff_id')
    if tech_id:
        tech_conflict = _check_staff_conflict(int(tech_id), start_time, end_time)
        if tech_conflict:
            tech = User.query.get(int(tech_id))
            flash(
                f'Staff conflict: {tech.first_name} {tech.last_name} is already assigned '
                f'{tech_conflict.start_time.strftime("%H:%M")}–{tech_conflict.end_time.strftime("%H:%M")} '
                f'for "{tech_conflict.submission.title}".',
                'error'
            )
            return redirect(url_for('schedule_views.schedule_page', day=day))

    usher_id = data.get('usher_id')
    if usher_id:
        usher_conflict = _check_staff_conflict(int(usher_id), start_time, end_time)
        if usher_conflict:
            usher = User.query.get(int(usher_id))
            flash(
                f'Staff conflict: {usher.first_name} {usher.last_name} is already assigned '
                f'{usher_conflict.start_time.strftime("%H:%M")}–{usher_conflict.end_time.strftime("%H:%M")} '
                f'for "{usher_conflict.submission.title}".',
                'error'
            )
            return redirect(url_for('schedule_views.schedule_page', day=day))
    # ────────────────────────────────────────────────────────────

    schedule = Schedule(
        submission_id=int(sub_id),
        room=data['room'],
        start_time=start_time,
        end_time=end_time,
        track_id=int(data['track_id'])
    )
    db.session.add(schedule)
    db.session.flush()

    # Assign staff
    if tech_id:
        db.session.add(StaffAssignment(schedule_id=schedule.id, staff_id=int(tech_id), role='TECH'))
    if usher_id:
        db.session.add(StaffAssignment(schedule_id=schedule.id, staff_id=int(usher_id), role='USHER'))

    db.session.commit()
    flash('Session scheduled successfully', 'success')
    return redirect(url_for('schedule_views.schedule_page', day=day))


# ── Update session ───────────────────────────────────────────────

@schedule_views.route('/schedule/update', methods=['POST'])
def update_schedule():
    data = request.form
    schedule_id = int(data['schedule_id'])
    schedule = Schedule.query.get_or_404(schedule_id)

    day = 1 if schedule.start_time.date() == DAY1.date() else 2
    base = DAY1 if day == 1 else DAY2

    try:
        sh, sm = map(int, data['start_time'].split(':'))
        eh, em = map(int, data['end_time'].split(':'))
        schedule.start_time = base.replace(hour=sh, minute=sm)
        schedule.end_time = base.replace(hour=eh, minute=em)
    except Exception:
        flash('Invalid time format', 'error')
        return redirect(url_for('schedule_views.schedule_page', day=day))

    schedule.room = data['room']
    schedule.track_id = int(data['track_id'])

    # ── Conflict checks (exclude this session itself) ────────────
    room_conflict = _check_room_conflict(schedule.room, schedule.start_time, schedule.end_time, exclude_id=schedule_id)
    if room_conflict:
        flash(
            f'Room conflict: {schedule.room} is already booked '
            f'{room_conflict.start_time.strftime("%H:%M")}–{room_conflict.end_time.strftime("%H:%M")} '
            f'for "{room_conflict.submission.title}".',
            'error'
        )
        db.session.rollback()
        return redirect(url_for('schedule_views.schedule_page', day=day))

    tech_id = data.get('tech_staff_id')
    if tech_id:
        tech_conflict = _check_staff_conflict(int(tech_id), schedule.start_time, schedule.end_time, exclude_id=schedule_id)
        if tech_conflict:
            tech = User.query.get(int(tech_id))
            flash(
                f'Staff conflict: {tech.first_name} {tech.last_name} is already assigned '
                f'{tech_conflict.start_time.strftime("%H:%M")}–{tech_conflict.end_time.strftime("%H:%M")} '
                f'for "{tech_conflict.submission.title}".',
                'error'
            )
            db.session.rollback()
            return redirect(url_for('schedule_views.schedule_page', day=day))

    usher_id = data.get('usher_id')
    if usher_id:
        usher_conflict = _check_staff_conflict(int(usher_id), schedule.start_time, schedule.end_time, exclude_id=schedule_id)
        if usher_conflict:
            usher = User.query.get(int(usher_id))
            flash(
                f'Staff conflict: {usher.first_name} {usher.last_name} is already assigned '
                f'{usher_conflict.start_time.strftime("%H:%M")}–{usher_conflict.end_time.strftime("%H:%M")} '
                f'for "{usher_conflict.submission.title}".',
                'error'
            )
            db.session.rollback()
            return redirect(url_for('schedule_views.schedule_page', day=day))
    # ────────────────────────────────────────────────────────────

    # Remove old staff assignments and re-add
    StaffAssignment.query.filter_by(schedule_id=schedule_id).delete()
    if tech_id:
        db.session.add(StaffAssignment(schedule_id=schedule_id, staff_id=int(tech_id), role='TECH'))
    if usher_id:
        db.session.add(StaffAssignment(schedule_id=schedule_id, staff_id=int(usher_id), role='USHER'))

    db.session.commit()
    flash('Session updated', 'success')
    return redirect(url_for('schedule_views.schedule_page', day=day))


# ── Delete session ───────────────────────────────────────────────

@schedule_views.route('/schedule/delete/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    day = 1 if schedule.start_time.date() == DAY1.date() else 2
    StaffAssignment.query.filter_by(schedule_id=schedule_id).delete()
    db.session.delete(schedule)
    db.session.commit()
    flash('Session deleted', 'success')
    return redirect(url_for('schedule_views.schedule_page', day=day))


# ── JSON API ─────────────────────────────────────────────────────

@schedule_views.route('/api/schedules', methods=['GET'])
def get_schedules_api():
    track_id = request.args.get('track_id')
    query = Schedule.query
    if track_id:
        query = query.filter_by(track_id=track_id)
    return jsonify([s.get_json() for s in query.order_by(Schedule.start_time).all()]), 200


@schedule_views.route('/api/schedules/<int:schedule_id>', methods=['GET'])
def get_schedule_api(schedule_id):
    s = Schedule.query.get_or_404(schedule_id)
    return jsonify(s.get_json()), 200
