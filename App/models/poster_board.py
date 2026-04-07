from App.database import db

class PosterBoard(db.Model):
    __tablename__ = "poster_boards"

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(256))
    #e.g A-1

    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"))