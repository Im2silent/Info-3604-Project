from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    logged_in = db.Column(db.Boolean, nullable=False, default=False)

    role = db.Column(db.String(50), nullable=False)
    #roles e.g ADMIN, REGULAR_USER

    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(256))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, first_name, last_name, email, password, role="REGULAR_USER"):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.set_password(password)
        self.role = role
        self.logged_in = False

    def get_json(self):
        return{
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role,
            'logged_in': self.logged_in
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def login(self, password):
        if self.check_password(password):
            self.logged_in = True
            db.session.commit()
            return True
        return False

    def logout(self):
        self.logged_in = False
        db.session.commit()
    

