from App.database import db

class StaffAssignment(db.Model):
    __tablename__ = "staff_assignments"

    id = db.Column(db.Integer, primary_key=True)

    schedule_id = db.Column(db.Integer, db.ForeignKey("schedules.id"))
    staff_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    role = db.Column(db.String(256))
    #USHER, TECH, 