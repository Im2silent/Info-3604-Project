from App.database import db

class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    abstract = db.Column(db.Text, nullable=False)

    presentation_type = db.Column(db.String(50))
    #ORAL or POSTER

    status = db.Column(db.String(50), default = "PENDING")
    #PENDING, SET

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"))