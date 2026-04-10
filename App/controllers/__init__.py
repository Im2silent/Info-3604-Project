from .auth_controller import auth_bp
from .checkin_controller import checkin_bp
from .poster_controller import poster_bp
from .review_controller import review_bp
from .schedule_controller import schedule_bp
from .submission_controller import submission_bp

blueprints = [
    auth_bp,
    checkin_bp,
    poster_bp,
    review_bp,
    schedule_bp,
    submission_bp,
]
