import os
from flask import Flask, render_template
from flask_cors import CORS

from App.database import init_db
from App.config import load_config
from App.controllers.auth_controller import auth_bp
from App.api.errors import register_error_handlers
from App.views import views, setup_admin


def add_views(app):
    for view in views:
        app.register_blueprint(view)


def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_views(app)
    init_db(app)
    setup_admin(app)
    register_error_handlers(app)
    app.app_context().push()
    return app
