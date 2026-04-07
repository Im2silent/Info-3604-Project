class PosterAssignment(db.Model):
    __tablename__ = "poster_assignments"

    id = db.Column(db.Integer, primary_key=True)

    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    board_id = db.Column(db.Integer, db.ForeignKey("poster_boards.id"))