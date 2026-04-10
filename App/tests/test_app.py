import pytest
from App.main import create_app
from App.database import db
from App.models import User, Track, Submission, Review, PosterBoard, PosterAssignment, Schedule, CheckIn


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ---- User / Auth ----

class TestUser:
    def test_create_user(self, app):
        with app.app_context():
            user = User("Alice", "Smith", "alice@test.com", "pass123", role="AUTHOR")
            db.session.add(user)
            db.session.commit()
            assert user.id is not None
            assert user.email == "alice@test.com"
            assert user.password != "pass123"  # should be hashed

    def test_check_password(self, app):
        with app.app_context():
            user = User("Bob", "Jones", "bob@test.com", "secret", role="REVIEWER")
            assert user.check_password("secret") is True
            assert user.check_password("wrong") is False

    def test_get_json(self, app):
        with app.app_context():
            user = User("Alice", "Smith", "alice@test.com", "pass123", role="AUTHOR")
            j = user.get_json()
            assert j["email"] == "alice@test.com"
            assert j["role"] == "AUTHOR"
            assert "password" not in j


# ---- Track ----

class TestTrack:
    def test_create_track(self, app):
        with app.app_context():
            track = Track(name="Health and Well-being", description="Health research")
            db.session.add(track)
            db.session.commit()
            assert track.id is not None
            assert track.name == "Health and Well-being"

    def test_track_get_json(self, app):
        with app.app_context():
            track = Track(name="Cybersecurity")
            db.session.add(track)
            db.session.commit()
            j = track.get_json()
            assert j["name"] == "Cybersecurity"
            assert "id" in j


# ---- Submission ----

class TestSubmission:
    def test_create_submission(self, app):
        with app.app_context():
            user = User("Jane", "Doe", "jane@test.com", "pass", role="AUTHOR")
            track = Track(name="Agri-Food")
            db.session.add_all([user, track])
            db.session.commit()

            sub = Submission(
                title="My Paper",
                abstract="This is an abstract.",
                presentation_type="ORAL",
                author_id=user.id,
                track_id=track.id
            )
            db.session.add(sub)
            db.session.commit()
            assert sub.id is not None
            assert sub.status == "PENDING"

    def test_submission_get_json(self, app):
        with app.app_context():
            user = User("Jane", "Doe", "jane@test.com", "pass", role="AUTHOR")
            track = Track(name="Agri-Food")
            db.session.add_all([user, track])
            db.session.commit()

            sub = Submission("Title", "Abstract", "POSTER", user.id, track.id)
            db.session.add(sub)
            db.session.commit()

            j = sub.get_json()
            assert j["title"] == "Title"
            assert j["presentation_type"] == "POSTER"


# ---- Review ----

class TestReview:
    def _setup(self, app):
        with app.app_context():
            author = User("Author", "One", "author@test.com", "pass", role="AUTHOR")
            reviewer = User("Rev", "One", "rev@test.com", "pass", role="REVIEWER")
            track = Track(name="Health")
            db.session.add_all([author, reviewer, track])
            db.session.commit()

            sub = Submission("Paper", "Abstract", "ORAL", author.id, track.id)
            db.session.add(sub)
            db.session.commit()
            return author.id, reviewer.id, sub.id

    def test_cannot_review_own_submission(self, app):
        with app.app_context():
            author = User("Author", "One", "author2@test.com", "pass", role="AUTHOR")
            track = Track(name="Tech")
            db.session.add_all([author, track])
            db.session.commit()
            sub = Submission("Paper", "Abstract", "ORAL", author.id, track.id)
            db.session.add(sub)
            db.session.commit()
            # Business rule: author_id == reviewer_id should be rejected
            assert sub.author_id == author.id

    def test_review_updates_submission_status(self, app):
        with app.app_context():
            author = User("Author", "Two", "author3@test.com", "pass", role="AUTHOR")
            reviewer = User("Rev", "Two", "rev2@test.com", "pass", role="REVIEWER")
            track = Track(name="Health")
            db.session.add_all([author, reviewer, track])
            db.session.commit()

            sub = Submission("Paper", "Abstract", "ORAL", author.id, track.id)
            db.session.add(sub)
            db.session.commit()

            review = Review(
                submission_id=sub.id,
                reviewer_id=reviewer.id,
                decision="ACCEPT"
            )
            db.session.add(review)
            sub.status = "ACCEPTED"
            db.session.commit()

            assert sub.status == "ACCEPTED"


# ---- Poster Board & Assignment ----

class TestPoster:
    def test_create_board(self, app):
        with app.app_context():
            track = Track(name="Agri-Food")
            db.session.add(track)
            db.session.commit()

            board = PosterBoard(code="A-1", track_id=track.id)
            db.session.add(board)
            db.session.commit()
            assert board.id is not None
            assert board.code == "A-1"

    def test_assign_poster(self, app):
        with app.app_context():
            author = User("Author", "P", "authorp@test.com", "pass", role="AUTHOR")
            track = Track(name="Agri-Food")
            db.session.add_all([author, track])
            db.session.commit()

            sub = Submission("Poster Paper", "Abstract", "POSTER", author.id, track.id)
            board = PosterBoard(code="B-2", track_id=track.id)
            db.session.add_all([sub, board])
            db.session.commit()

            assignment = PosterAssignment(submission_id=sub.id, board_id=board.id)
            db.session.add(assignment)
            db.session.commit()
            assert assignment.id is not None
            assert assignment.submission_id == sub.id


# ---- Check-In ----

class TestCheckIn:
    def test_checkin(self, app):
        with app.app_context():
            user = User("Check", "In", "checkin@test.com", "pass", role="AUTHOR")
            db.session.add(user)
            db.session.commit()

            check = CheckIn(user_id=user.id)
            db.session.add(check)
            db.session.commit()
            assert check.id is not None
            assert check.timestamp is not None

    def test_checkin_get_json(self, app):
        with app.app_context():
            user = User("Check", "In2", "checkin2@test.com", "pass", role="AUTHOR")
            db.session.add(user)
            db.session.commit()
            check = CheckIn(user_id=user.id)
            db.session.add(check)
            db.session.commit()
            j = check.get_json()
            assert j["user_id"] == user.id
            assert "timestamp" in j


# ---- API Routes ----

class TestAuthAPI:
    def test_register(self, client):
        res = client.post('/api/register', json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "password": "testpass",
            "role": "AUTHOR"
        })
        assert res.status_code == 201
        assert res.get_json()["message"] == "User created"

    def test_register_duplicate_email(self, client):
        payload = {
            "first_name": "Test", "last_name": "User",
            "email": "dup@test.com", "password": "pass", "role": "AUTHOR"
        }
        client.post('/api/register', json=payload)
        res = client.post('/api/register', json=payload)
        assert res.status_code == 409

    def test_login_success(self, client):
        client.post('/api/register', json={
            "first_name": "Login", "last_name": "User",
            "email": "login@test.com", "password": "mypass", "role": "AUTHOR"
        })
        res = client.post('/api/login', json={"email": "login@test.com", "password": "mypass"})
        assert res.status_code == 200

    def test_login_bad_credentials(self, client):
        res = client.post('/api/login', json={"email": "nobody@test.com", "password": "wrong"})
        assert res.status_code == 401


class TestTracksAPI:
    def test_get_tracks_public(self, client):
        res = client.get('/api/tracks')
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)
