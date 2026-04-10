from .index import index_views
from .auth import auth_views
from .user_views import user_views
from .track_views import track_views
from .submission_views import submission_views
from .review_views import review_views
from .schedule_views import schedule_views
from .poster_views import poster_views
from .checkin_views import checkin_views
from .admin import setup_admin

views = [
    index_views,
    auth_views,
    user_views,
    track_views,
    submission_views,
    review_views,
    schedule_views,
    poster_views,
    checkin_views,
]
