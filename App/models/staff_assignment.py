from App.database import db

class StaffAssignment(db.Model):
    __tablename__ = "staff_assignments"

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("schedules.id"))
    staff_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    role = db.Column(db.String(256))
    schedule = db.relationship("Schedule", backref="staff_assignments")
    staff = db.relationship("User", backref="staff_assignments")

    def __init__(self, schedule_id, staff_id, role):
        self.schedule_id = schedule_id
        self.staff_id = staff_id
        self.role = role

    def get_json(self):
        return {
            "id": self.id,
            "schedule_id": self.schedule_id,
            "staff_id": self.staff_id,
            "role": self.role
        }