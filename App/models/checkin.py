from datetime import datetime
from App.database import db

class CheckIn(db.Model):
    __tablename__ = "checkins"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime)

    user = db.relationship("User", backref="checkins")

    def __init__(self, user_id, timestamp=None):
        self.user_id = user_id
        self.timestamp = timestamp or datetime.utcnow()

    def get_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }