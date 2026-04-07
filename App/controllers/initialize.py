from App.database import db
from App.models import User, Track


def initialize():
    db.drop_all()
    db.create_all()

    # 🔹 Create Admin User
    admin = User(
        first_name="Admin",
        last_name="User",
        email="admin@test.com",
        password="admin123",
        role="ADMIN"
    )

    # 🔹 Create Sample Users
    reviewer = User(
        first_name="Review",
        last_name="User",
        email="reviewer@test.com",
        password="review123",
        role="REVIEWER"
    )

    presenter = User(
        first_name="Present",
        last_name="User",
        email="presenter@test.com",
        password="present123",
        role="PRESENTER"
    )

    db.session.add_all([admin, reviewer, presenter])
    db.session.commit()

    # 🔹 Create Tracks (Themes)
    track1 = Track(name="Cybersecurity")
    track2 = Track(name="Artificial Intelligence")
    track3 = Track(name="Software Engineering")

    db.session.add_all([track1, track2, track3])
    db.session.commit()

    print("Database initialized with sample data.")