from App.database import db

class Track(db.Model):
    __tablename__ = "tracks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(32), default="#6c757d")  

    def __init__(self, name, description=None, color="#6c757d"):
        self.name = name
        self.description = description
        self.color = color

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color
        }