from App.database import db
from datetime import datetime

class Judging(db.Model):
    __tablename__ = "judging"

    id = db.Column(db.Integer, primary_key=True)

    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    judge_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submission = db.relationship("Submission", backref="judgings")
    judge = db.relationship("User", backref="judgings")

    def __init__(self, submission_id, judge_id, score=None, feedback=None):
        self.submission_id = submission_id
        self.judge_id = judge_id
        self.score = score
        self.feedback = feedback

    def get_json(self):
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "judge_id": self.judge_id,
            "score": self.score,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }