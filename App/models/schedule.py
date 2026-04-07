class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)

    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))

    room = db.Column(db.String(256))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"))