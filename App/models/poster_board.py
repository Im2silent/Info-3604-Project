from App.database import db

class PosterBoard(db.Model):
    __tablename__ = "poster_boards"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(256))
    track_id = db.Column(db.Integer, db.ForeignKey("tracks.id"))
    color = db.Column(db.String(32), default="#6c757d")     # hex color, matches theme
    cell_width = db.Column(db.Integer, default=1)           # how many grid columns it spans
    cell_height = db.Column(db.Integer, default=1)          # how many grid rows it spans

    track = db.relationship("Track", backref="poster_boards")

    def __init__(self, code, track_id, color="#6c757d", cell_width=1, cell_height=1):
        self.code = code
        self.track_id = track_id
        self.color = color
        self.cell_width = cell_width
        self.cell_height = cell_height

    def get_json(self):
        assignment = self.assignments[0] if self.assignments else None
        return {
            "id": self.id,
            "code": self.code,
            "track_id": self.track_id,
            "color": self.color,
            "cell_width": self.cell_width,
            "cell_height": self.cell_height,
            "submission_id": assignment.submission_id if assignment else None,
            "submission_title": assignment.submission.title if assignment and assignment.submission else None,
        }