from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import jwt_required, current_user
from flask_admin import Admin
from flask import flash, redirect, url_for, request
from App.database import db
from App.models import User, Track, Submission, Schedule, PosterBoard, PosterAssignment, Review, CheckIn


class SecureModelView(ModelView):
    @jwt_required()
    def is_accessible(self):
        return current_user is not None and current_user.role == "ADMIN"

    def inaccessible_callback(self, name, **kwargs):
        flash("Admin access required.")
        return redirect(url_for('index_views.index_page', next=request.url))


def setup_admin(app):
    admin = Admin(app, name='Principal Awards Admin', template_mode='bootstrap3')
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(Track, db.session))
    admin.add_view(SecureModelView(Submission, db.session))
    admin.add_view(SecureModelView(Schedule, db.session))
    admin.add_view(SecureModelView(PosterBoard, db.session))
    admin.add_view(SecureModelView(PosterAssignment, db.session))
    admin.add_view(SecureModelView(Review, db.session))
    admin.add_view(SecureModelView(CheckIn, db.session))
