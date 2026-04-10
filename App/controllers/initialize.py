from App.database import db
from App.models import User, Track, Submission, PosterBoard, Schedule, StaffAssignment, CheckIn
from datetime import datetime


def initialize():
    db.drop_all()
    db.create_all()

    # --- Users ---
    admin = User(first_name="Admin", last_name="User", email="admin@awards.com", password="adminpass", role="ADMIN")
    chair = User(first_name="Conference", last_name="Chair", email="chair@awards.com", password="chairpass", role="CHAIR")
    reviewer1 = User(first_name="Alice", last_name="Thomas", email="alice@awards.com", password="alicepass", role="REVIEWER")
    reviewer2 = User(first_name="Bob", last_name="Ramkhelawan", email="bob@awards.com", password="bobpass", role="REVIEWER")
    tech1 = User(first_name="Taylor", last_name="Baptiste", email="taylor@awards.com", password="taylorpass", role="TECH")
    tech2 = User(first_name="Marcus", last_name="Williams", email="marcus@awards.com", password="marcuspass", role="TECH")
    usher1 = User(first_name="Jane", last_name="Doe", email="jane@awards.com", password="janepass", role="USHER")
    usher2 = User(first_name="Kevin", last_name="Singh", email="kevin@awards.com", password="kevinpass", role="USHER")
    author1 = User(first_name="John", last_name="Doe", email="john@awards.com", password="johnpass", role="AUTHOR")
    author2 = User(first_name="Priya", last_name="Ramsaran", email="priya@awards.com", password="priyapass", role="AUTHOR")
    author3 = User(first_name="Marcus", last_name="St. Hill", email="marcus2@awards.com", password="marcuspass2", role="AUTHOR")
    author4 = User(first_name="Latoya", last_name="Ferguson", email="latoya@awards.com", password="latoyapass", role="AUTHOR")
    db.session.add_all([admin, chair, reviewer1, reviewer2, tech1, tech2, usher1, usher2,
                        author1, author2, author3, author4])
    db.session.commit()

    # --- Tracks with distinct colors ---
    track1 = Track(name="i. Agri-Food Technology and Policy for Food and Nutrition Security",
                   description="Research on agriculture, food systems, and nutrition policy.",
                   color="#2d8a4e")   # green
    track2 = Track(name="ii. Health and Well-being Issues and Advances",
                   description="Research on health outcomes, medical advances, and well-being.",
                   color="#c0392b")   # red
    track3 = Track(name="iii. Cybersecurity and Digital Infrastructure",
                   description="Research on cybersecurity, operating systems, and digital systems.",
                   color="#1a5276")   # dark blue
    track4 = Track(name="iv. Emerging Technologies: AI, LLMs and Social Media",
                   description="Research on AI, LLMs, blockchain, and social media.",
                   color="#7d3c98")   # purple
    db.session.add_all([track1, track2, track3, track4])
    db.session.commit()

    # --- Submissions ---
    # ORAL submissions (accepted so they can be scheduled)
    oral1 = Submission(title="Sustainable Farming with AI",
                       abstract="This paper explores how artificial intelligence can transform sustainable farming practices in the Caribbean.",
                       presentation_type="ORAL", author_id=author1.id, track_id=track1.id)
    oral1.status = "ACCEPTED"

    oral2 = Submission(title="Digital Twin Technologies in Crop Monitoring",
                       abstract="An exploration of digital twin technology for real-time crop monitoring and yield optimization.",
                       presentation_type="ORAL", author_id=author2.id, track_id=track1.id)
    oral2.status = "ACCEPTED"

    oral3 = Submission(title="Ransomware Trends in Caribbean Healthcare",
                       abstract="Analysis of ransomware attack patterns targeting healthcare institutions across the Caribbean.",
                       presentation_type="ORAL", author_id=author3.id, track_id=track3.id)
    oral3.status = "ACCEPTED"

    oral4 = Submission(title="LLM Integration in Academic Research",
                       abstract="Examining the impact and ethical implications of large language models in academic research workflows.",
                       presentation_type="ORAL", author_id=author4.id, track_id=track4.id)
    oral4.status = "ACCEPTED"

    oral5 = Submission(title="Telomere Research and Longevity Outcomes",
                       abstract="A study correlating telomere length with lifestyle factors and longevity outcomes in Caribbean populations.",
                       presentation_type="ORAL", author_id=author2.id, track_id=track2.id)
    oral5.status = "ACCEPTED"

    # POSTER submissions (accepted)
    poster1 = Submission(title="Crop Yield Prediction Models in T&T",
                         abstract="A study on using ML models to predict crop yields in Trinidad and Tobago.",
                         presentation_type="POSTER", author_id=author1.id, track_id=track1.id)
    poster1.status = "ACCEPTED"

    poster2 = Submission(title="Soil Health Indices for Sustainable Cocoa Farming",
                         abstract="Measuring soil microbiome diversity as an indicator of sustainable cocoa production.",
                         presentation_type="POSTER", author_id=author2.id, track_id=track1.id)
    poster2.status = "ACCEPTED"

    poster3 = Submission(title="Zero-Trust Architecture in Government Networks",
                         abstract="Implementation strategies for zero-trust network architecture in government institutions.",
                         presentation_type="POSTER", author_id=author3.id, track_id=track3.id)
    poster3.status = "ACCEPTED"

    poster4 = Submission(title="Blockchain for Academic Credential Verification",
                         abstract="Using distributed ledger technology to verify and share academic credentials securely.",
                         presentation_type="POSTER", author_id=author4.id, track_id=track4.id)
    poster4.status = "ACCEPTED"

    poster5 = Submission(title="Mental Health Apps: Efficacy in Young Adults",
                         abstract="A systematic review of mental health applications and their clinical efficacy in young adults aged 18-30.",
                         presentation_type="POSTER", author_id=author1.id, track_id=track2.id)
    poster5.status = "ACCEPTED"

    # PENDING submissions (not yet reviewed)
    pending1 = Submission(title="Hydroponic Systems for Urban Food Production",
                          abstract="Evaluating the viability of hydroponic farming for urban food security in Port of Spain.",
                          presentation_type="POSTER", author_id=author3.id, track_id=track1.id)

    db.session.add_all([oral1, oral2, oral3, oral4, oral5,
                        poster1, poster2, poster3, poster4, poster5, pending1])
    db.session.commit()

    # --- Schedules (2-day event: Nov 26-27) ---
    # Day 1 - Nov 26
    sched1 = Schedule(submission_id=oral1.id, room="JFK Auditorium",
                      start_time=datetime(2025, 11, 26, 9, 0),
                      end_time=datetime(2025, 11, 26, 9, 30),
                      track_id=track1.id)
    sched2 = Schedule(submission_id=oral2.id, room="JFK Auditorium",
                      start_time=datetime(2025, 11, 26, 9, 30),
                      end_time=datetime(2025, 11, 26, 10, 0),
                      track_id=track1.id)
    sched3 = Schedule(submission_id=oral5.id, room="Lecture Room A",
                      start_time=datetime(2025, 11, 26, 10, 0),
                      end_time=datetime(2025, 11, 26, 10, 30),
                      track_id=track2.id)
    # Day 2 - Nov 27
    sched4 = Schedule(submission_id=oral3.id, room="JFK Auditorium",
                      start_time=datetime(2025, 11, 27, 9, 0),
                      end_time=datetime(2025, 11, 27, 9, 30),
                      track_id=track3.id)
    sched5 = Schedule(submission_id=oral4.id, room="Lecture Room B",
                      start_time=datetime(2025, 11, 27, 10, 0),
                      end_time=datetime(2025, 11, 27, 10, 30),
                      track_id=track4.id)

    db.session.add_all([sched1, sched2, sched3, sched4, sched5])
    db.session.commit()

    # --- Staff assignments ---
    db.session.add_all([
        StaffAssignment(schedule_id=sched1.id, staff_id=tech1.id, role="TECH"),
        StaffAssignment(schedule_id=sched1.id, staff_id=usher1.id, role="USHER"),
        StaffAssignment(schedule_id=sched2.id, staff_id=tech1.id, role="TECH"),
        StaffAssignment(schedule_id=sched2.id, staff_id=usher2.id, role="USHER"),
        StaffAssignment(schedule_id=sched4.id, staff_id=tech2.id, role="TECH"),
        StaffAssignment(schedule_id=sched4.id, staff_id=usher1.id, role="USHER"),
        StaffAssignment(schedule_id=sched5.id, staff_id=tech2.id, role="TECH"),
        StaffAssignment(schedule_id=sched5.id, staff_id=usher2.id, role="USHER"),
    ])
    db.session.commit()

    # --- Poster boards: 13-column grid ---
    # Each track gets boards labeled col-row (A-1, A-2, B-1 etc.)
    # track1 = green, track2 = red, track3 = blue, track4 = purple
    cols = [chr(c) for c in range(ord('A'), ord('N'))]  # A-M = 13 columns
    for col in cols:
        for row in range(1, 7):   # 6 rows
            board = PosterBoard(code=f"{col}-{row}", track_id=track1.id,
                                color=track1.color, cell_width=1, cell_height=1)
            db.session.add(board)
    db.session.commit()

    print("Database initialized successfully for Principal Awards & Research Festival 2025!")
