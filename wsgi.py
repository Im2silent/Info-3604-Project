import click, pytest, sys
from flask.cli import AppGroup
from flask_migrate import Migrate, upgrade

from App.database import db, get_migrate
from App.models import User, Track, Submission, Review, PosterBoard, PosterAssignment, Schedule, StaffAssignment, CheckIn
from App.main import create_app
from App.controllers.initialize import initialize

app = create_app()
migrate = get_migrate(app)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

@app.cli.command("init", help="Drop, recreate and seed the database")
def init():
    initialize()
    print("Database initialised for Principal Awards & Research Festival!")


# ---------------------------------------------------------------------------
# User commands
# ---------------------------------------------------------------------------
user_cli = AppGroup('user', help='User management commands')


@user_cli.command("list", help="List all users")
@click.option("--role", default=None, help="Filter by role (ADMIN, AUTHOR, REVIEWER, TECH, USHER, CHAIR)")
def list_users(role):
    query = User.query
    if role:
        query = query.filter_by(role=role.upper())
    users = query.all()
    if not users:
        print("No users found.")
        return
    print(f"\n{'ID':<6} {'Name':<25} {'Email':<30} {'Role':<15}")
    print("-" * 76)
    for u in users:
        print(f"{u.id:<6} {u.first_name + ' ' + u.last_name:<25} {u.email:<30} {u.role:<15}")
    print()


@user_cli.command("create", help="Create a new user")
@click.argument("first_name")
@click.argument("last_name")
@click.argument("email")
@click.argument("password")
@click.argument("role", default="AUTHOR")
def create_user(first_name, last_name, email, password, role):
    if User.query.filter_by(email=email).first():
        print(f"Error: email '{email}' is already registered.")
        return
    user = User(first_name=first_name, last_name=last_name,
                email=email, password=password, role=role.upper())
    db.session.add(user)
    db.session.commit()
    print(f"User {first_name} {last_name} ({role}) created with ID {user.id}.")


@user_cli.command("delete", help="Delete a user by ID")
@click.argument("user_id", type=int)
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        print(f"No user with ID {user_id}.")
        return
    db.session.delete(user)
    db.session.commit()
    print(f"User {user_id} deleted.")


app.cli.add_command(user_cli)


# ---------------------------------------------------------------------------
# Track commands
# ---------------------------------------------------------------------------
track_cli = AppGroup('track', help='Conference track commands')


@track_cli.command("list", help="List all tracks")
def list_tracks():
    tracks = Track.query.all()
    if not tracks:
        print("No tracks found.")
        return
    print(f"\n{'ID':<6} {'Name':<60} {'Description'}")
    print("-" * 90)
    for t in tracks:
        desc = (t.description or "")[:40]
        print(f"{t.id:<6} {t.name:<60} {desc}")
    print()


@track_cli.command("create", help="Create a new track")
@click.argument("name")
@click.option("--description", default=None)
def create_track(name, description):
    from App.models.track import Track as TrackModel
    track = TrackModel(name=name, description=description)
    db.session.add(track)
    db.session.commit()
    print(f"Track '{name}' created with ID {track.id}.")


app.cli.add_command(track_cli)


# ---------------------------------------------------------------------------
# Submission commands
# ---------------------------------------------------------------------------
submission_cli = AppGroup('submission', help='Submission commands')


@submission_cli.command("list", help="List all submissions")
@click.option("--status", default=None, help="Filter by status (PENDING, ACCEPTED, REJECTED, REVISION)")
@click.option("--track", default=None, type=int, help="Filter by track ID")
@click.option("--type", "ptype", default=None, help="Filter by type (ORAL, POSTER)")
def list_submissions(status, track, ptype):
    query = Submission.query
    if status:
        query = query.filter_by(status=status.upper())
    if track:
        query = query.filter_by(track_id=track)
    if ptype:
        query = query.filter_by(presentation_type=ptype.upper())
    subs = query.all()
    if not subs:
        print("No submissions found.")
        return
    print(f"\n{'ID':<6} {'Title':<35} {'Type':<8} {'Status':<12} {'Track':<6} {'Author':<6}")
    print("-" * 73)
    for s in subs:
        print(f"{s.id:<6} {s.title[:33]:<35} {s.presentation_type:<8} {s.status:<12} {s.track_id:<6} {s.author_id:<6}")
    print()


@submission_cli.command("accept", help="Accept a submission by ID")
@click.argument("submission_id", type=int)
def accept_submission(submission_id):
    sub = Submission.query.get(submission_id)
    if not sub:
        print(f"No submission with ID {submission_id}.")
        return
    sub.status = "ACCEPTED"
    db.session.commit()
    print(f"Submission {submission_id} accepted.")


@submission_cli.command("reject", help="Reject a submission by ID")
@click.argument("submission_id", type=int)
def reject_submission(submission_id):
    sub = Submission.query.get(submission_id)
    if not sub:
        print(f"No submission with ID {submission_id}.")
        return
    sub.status = "REJECTED"
    db.session.commit()
    print(f"Submission {submission_id} rejected.")


app.cli.add_command(submission_cli)


# ---------------------------------------------------------------------------
# Schedule commands
# ---------------------------------------------------------------------------
schedule_cli = AppGroup('schedule', help='Schedule management commands')


@schedule_cli.command("list", help="List all scheduled sessions")
@click.option("--track", default=None, type=int, help="Filter by track ID")
def list_schedules(track):
    query = Schedule.query
    if track:
        query = query.filter_by(track_id=track)
    schedules = query.all()
    if not schedules:
        print("No schedules found.")
        return
    print(f"\n{'ID':<6} {'Submission':<12} {'Room':<20} {'Start':<22} {'End':<22} {'Track':<6}")
    print("-" * 88)
    for s in schedules:
        start = s.start_time.strftime("%Y-%m-%d %H:%M") if s.start_time else "N/A"
        end = s.end_time.strftime("%Y-%m-%d %H:%M") if s.end_time else "N/A"
        print(f"{s.id:<6} {s.submission_id:<12} {s.room:<20} {start:<22} {end:<22} {s.track_id:<6}")
    print()


@schedule_cli.command("assign_staff", help="Assign a staff member to a schedule")
@click.argument("schedule_id", type=int)
@click.argument("staff_id", type=int)
@click.argument("role")
def assign_staff(schedule_id, staff_id, role):
    role = role.upper()
    if role not in ("USHER", "TECH"):
        print("Role must be USHER or TECH.")
        return
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        print(f"No schedule with ID {schedule_id}.")
        return
    staff = User.query.get(staff_id)
    if not staff:
        print(f"No user with ID {staff_id}.")
        return
    assignment = StaffAssignment(schedule_id=schedule_id, staff_id=staff_id, role=role)
    db.session.add(assignment)
    db.session.commit()
    print(f"{staff.first_name} {staff.last_name} assigned as {role} to schedule {schedule_id}.")


app.cli.add_command(schedule_cli)


# ---------------------------------------------------------------------------
# Poster commands
# ---------------------------------------------------------------------------
poster_cli = AppGroup('poster', help='Poster board and assignment commands')


@poster_cli.command("list_boards", help="List poster boards")
@click.option("--track", default=None, type=int, help="Filter by track ID")
def list_boards(track):
    query = PosterBoard.query
    if track:
        query = query.filter_by(track_id=track)
    boards = query.order_by(PosterBoard.code).all()
    if not boards:
        print("No boards found.")
        return
    taken = {a.board_id for a in PosterAssignment.query.all()}
    print(f"\n{'ID':<6} {'Code':<10} {'Track':<6} {'Status'}")
    print("-" * 35)
    for b in boards:
        status = "TAKEN" if b.id in taken else "FREE"
        print(f"{b.id:<6} {b.code:<10} {b.track_id:<6} {status}")
    print()


@poster_cli.command("list_assignments", help="List poster assignments")
def list_assignments():
    assignments = PosterAssignment.query.all()
    if not assignments:
        print("No assignments found.")
        return
    print(f"\n{'ID':<6} {'Submission':<12} {'Board':<8} {'Board Code'}")
    print("-" * 40)
    for a in assignments:
        board = PosterBoard.query.get(a.board_id)
        print(f"{a.id:<6} {a.submission_id:<12} {a.board_id:<8} {board.code if board else 'N/A'}")
    print()


app.cli.add_command(poster_cli)


# ---------------------------------------------------------------------------
# Check-in commands
# ---------------------------------------------------------------------------
checkin_cli = AppGroup('checkin', help='Participant check-in commands')


@checkin_cli.command("list", help="List all check-ins")
@click.option("--date", default=None, help="Filter by date YYYY-MM-DD")
def list_checkins(date):
    from datetime import datetime
    query = CheckIn.query
    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(db.func.date(CheckIn.timestamp) == d)
        except ValueError:
            print("Date must be in YYYY-MM-DD format.")
            return
    checkins = query.all()
    if not checkins:
        print("No check-ins found.")
        return
    print(f"\n{'ID':<6} {'User ID':<10} {'Timestamp'}")
    print("-" * 40)
    for c in checkins:
        ts = c.timestamp.strftime("%Y-%m-%d %H:%M:%S") if c.timestamp else "N/A"
        print(f"{c.id:<6} {c.user_id:<10} {ts}")
    print()


@checkin_cli.command("checkin", help="Manually check in a user by ID")
@click.argument("user_id", type=int)
def manual_checkin(user_id):
    from datetime import datetime
    user = User.query.get(user_id)
    if not user:
        print(f"No user with ID {user_id}.")
        return
    check = CheckIn(user_id=user_id)
    db.session.add(check)
    db.session.commit()
    print(f"User {user.first_name} {user.last_name} checked in at {check.timestamp}.")


app.cli.add_command(checkin_cli)


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------
test_cli = AppGroup('test', help='Run test suite')


@test_cli.command("all", help="Run all tests")
def run_all():
    sys.exit(pytest.main(["-v", "App/tests/"]))


@test_cli.command("models", help="Run model unit tests")
def run_models():
    sys.exit(pytest.main(["-v", "-k", "TestUser or TestTrack or TestSubmission or TestReview or TestPoster or TestCheckIn"]))


@test_cli.command("api", help="Run API integration tests")
def run_api():
    sys.exit(pytest.main(["-v", "-k", "TestAuthAPI or TestTracksAPI"]))


app.cli.add_command(test_cli)
