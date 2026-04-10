from App.database import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    score = db.Column(db.Float)
    comments = db.Column(db.Text)
    decision = db.Column(db.String(256))
    created_at = db.Column(db.DateTime)
    submission = db.relationship("Submission", backref="reviews")
    reviewer = db.relationship("User", backref="reviews")

    def __init__(self, submission_id, reviewer_id, score=None, comments=None, decision=None):
        self.submission_id = submission_id
        self.reviewer_id = reviewer_id
        self.score = score
        self.comments = comments
        self.decision = decision

    def get_json(self):
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "reviewer_id": self.reviewer_id,
            "score": self.score,
            "comments": self.comments,
            "decision": self.decision,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }