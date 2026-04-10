from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from App.models.checkin import CheckIn
from App.models.user import User
from App.models.schedule import Schedule
from App.models.track import Track
from App.database import db
from datetime import datetime, date

checkin_views = Blueprint('checkin_views', __name__)

DAY1 = date(2025, 11, 26)
DAY2 = date(2025, 11, 27)


@checkin_views.route('/checkin', methods=['GET'])
def checkin_page():
    day = int(request.args.get('day', 1))
    day_dt = DAY1 if day == 1 else DAY2

    # Sessions for this day
    all_schedules = Schedule.query.order_by(Schedule.start_time).all()
    day_schedules = [s for s in all_schedules if s.start_time.date() == day_dt]

    # Who has checked in today
    today = date.today()
    todays_checkins = CheckIn.query.filter(
        db.func.date(CheckIn.timestamp) == today
    ).all()
    checked_in_ids = {c.user_id for c in todays_checkins}

    all_users = User.query.order_by(User.first_name).all()
    total_participants = len(all_users)

    return render_template('checkin.html',
        active_page='checkin',
        active_day=day,
        active_day_schedules=day_schedules,
        checked_in_ids=checked_in_ids,
        checkin_count=len(todays_checkins),
        total_participants=total_participants,
        all_users=all_users,
        today=today.strftime('%A, %d %B %Y'),
        all_tracks=Track.query.all(),
    )


@checkin_views.route('/checkin/do', methods=['POST'])
def do_checkin():
    user_id = request.form.get('user_id')
    if not user_id:
        flash('Missing user_id', 'error')
        return redirect(url_for('checkin_views.checkin_page'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('checkin_views.checkin_page'))

    # Prevent duplicate check-in today
    today = date.today()
    existing = CheckIn.query.filter(
        CheckIn.user_id == int(user_id),
        db.func.date(CheckIn.timestamp) == today
    ).first()

    if existing:
        flash(f'{user.first_name} {user.last_name} already checked in today', 'info')
    else:
        check = CheckIn(user_id=int(user_id))
        db.session.add(check)
        db.session.commit()
        flash(f'{user.first_name} {user.last_name} checked in successfully', 'success')

    return redirect(url_for('checkin_views.checkin_page'))


@checkin_views.route('/api/checkins', methods=['GET'])
def get_checkins_api():
    checkins = CheckIn.query.all()
    return jsonify([c.get_json() for c in checkins]), 200
