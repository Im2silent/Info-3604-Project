from flask import Blueprint, render_template, jsonify, redirect, url_for
from App.controllers.initialize import initialize
from App.models import Track, Submission, Schedule, CheckIn

index_views = Blueprint('index_views', __name__, template_folder='../templates')

def get_all_tracks():
    return Track.query.all()

@index_views.route('/', methods=['GET'])
def index_page():
    tracks = get_all_tracks()
    total = Submission.query.count()
    accepted = Submission.query.filter_by(status='ACCEPTED').count()
    scheduled = Schedule.query.count()
    return render_template('index.html',
        all_tracks=tracks,
        total_submissions=total,
        accepted_submissions=accepted,
        scheduled_count=scheduled,
        active_page='home'
    )

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return redirect(url_for('index_views.index_page'))

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})
