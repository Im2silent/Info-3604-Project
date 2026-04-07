class Judging(db.Model):
    __tablename__ = "judging"

    id = db.Column(db.Integer, primary_key=True)

    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    judge_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    score = db.Column(db.Float)
    feedback = db.Column(db.Text)