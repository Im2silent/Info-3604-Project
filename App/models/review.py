from App.database import db

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)

    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"))
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    score = db.Column(db.Float)
    comments = db.Column(db.Text)

    decision = db.Column(db.String(256))
    #ACCEPT, REJECT

    created_at = db.Column(db.DateTime)