from App.database import db
from datetime import datetime

class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    presentation_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default = "PENDING")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.relationship("User", backref="submissions")
    track = db.relationship("Track", backref="submissions")

    def __init__(self, title, abstract, presentation_type, author_id, track_id):
        self.title = title
        self.abstract = abstract
        self.presentation_type = presentation_type
        self.author_id = author_id
        self.track_id = track_id

    def get_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "abstract": self.abstract,
            "presentation_type": self.presentation_type,
            "status": self.status,
            "author_id": self.author_id,
            "track_id": self.track_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }