from App.database import db

class PosterAssignment(db.Model):
    __tablename__ = "poster_assignments"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    board_id = db.Column(db.Integer, db.ForeignKey("poster_boards.id"))
    submission = db.relationship("Submission", backref="poster_assignment", uselist=False)
    board = db.relationship("PosterBoard", backref="assignments")

    def __init__(self, submission_id, board_id):
        self.submission_id = submission_id
        self.board_id = board_id

    def get_json(self):
        return {
            "id": self.id,
            "submission_id": self.submission_id,
            "board_id": self.board_id
        }