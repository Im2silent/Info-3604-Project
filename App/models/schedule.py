from App.database import db

class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    room = db.Column(db.String(256))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"))
    submission = db.relationship("Submission", backref="schedule", uselist=False)
    track = db.relationship("Track", backref="schedules")

    def __init__(self, submission_id, room, start_time, end_time, track_id):
        self.submission_id = submission_id
        self.room = room
        self.start_time = start_time
        self.end_time = end_time
        self.track_id = track_id

    def get_json(self):
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "room": self.room,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "track_id": self.track_id
        }