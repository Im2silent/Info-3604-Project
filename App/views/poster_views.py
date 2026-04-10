from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from App.models.poster_board import PosterBoard
from App.models.poster_assignment import PosterAssignment
from App.models.submission import Submission
from App.models.track import Track
from App.database import db
import json

poster_views = Blueprint('poster_views', __name__)

DEFAULT_COLS = 13
DEFAULT_ROWS = 6
LETTERS = [chr(65 + i) for i in range(26)]


def _parse_size(size_str):
    try:
        parts = size_str.lower().replace('x', 'x').split('x')
        return int(parts[0]), int(parts[1])
    except Exception:
        return DEFAULT_COLS, DEFAULT_ROWS


# ── HTML page ────────────────────────────────────────────────────

@poster_views.route('/posters', methods=['GET'])
def posters_page():
    size = request.args.get('size', f'{DEFAULT_COLS}x{DEFAULT_ROWS}')
    active_tab = request.args.get('tab', 'poster')
    track_id_filter = request.args.get('track_id')

    cols, rows = _parse_size(size)
    col_letters = LETTERS[:cols]

    # All boards — ensure they exist for this grid size
    all_boards = PosterBoard.query.order_by(PosterBoard.code).all()
    boards_by_code = {b.code: b for b in all_boards}

    # Build boards_json for the JS grid
    boards_json = {}
    for b in all_boards:
        assignment = b.assignments[0] if b.assignments else None
        boards_json[b.code] = {
            'id': b.id,
            'color': b.color,
            'cell_width': b.cell_width,
            'cell_height': b.cell_height,
            'submission_id': assignment.submission_id if assignment else None,
            'submission_title': assignment.submission.title if assignment and assignment.submission else None,
        }

    # Poster submissions (accepted, POSTER type)
    poster_query = Submission.query.filter_by(presentation_type='POSTER', status='ACCEPTED')
    if track_id_filter:
        poster_query = poster_query.filter_by(track_id=track_id_filter)
    poster_submissions = poster_query.all()

    # Which submissions are already placed
    placed_ids = set(
        a.submission_id for a in PosterAssignment.query.all()
    )

    assignments = PosterAssignment.query.all()

    return render_template('posters.html',
        active_page='posters',
        active_tab=active_tab,
        cols=cols,
        rows=rows,
        boards_json=json.dumps(boards_json),
        boards=all_boards,
        poster_submissions=poster_submissions,
        placed_ids=placed_ids,
        assignments=assignments,
        assigned_count=len(assignments),
        all_tracks=Track.query.all(),
    )


# ── Assign poster to board ────────────────────────────────────────

@poster_views.route('/posters/assign', methods=['POST'])
def assign_poster():
    data = request.form
    sub_id = data.get('submission_id')
    board_id = data.get('board_id')
    cell_w = int(data.get('cell_width', 1))
    cell_h = int(data.get('cell_height', 1))
    color = data.get('color', '#6c757d')

    if not sub_id or not board_id:
        flash('Missing submission or board', 'error')
        return redirect(url_for('poster_views.posters_page'))

    submission = Submission.query.get(sub_id)
    board = PosterBoard.query.get(board_id)

    if not submission or not board:
        flash('Submission or board not found', 'error')
        return redirect(url_for('poster_views.posters_page'))

    if PosterAssignment.query.filter_by(board_id=board_id).first():
        flash('Board spot is already assigned', 'error')
        return redirect(url_for('poster_views.posters_page'))

    if PosterAssignment.query.filter_by(submission_id=sub_id).first():
        flash('Submission is already placed on a board', 'error')
        return redirect(url_for('poster_views.posters_page'))

    # Update board dimensions and color
    board.cell_width = cell_w
    board.cell_height = cell_h
    board.color = color

    assignment = PosterAssignment(submission_id=int(sub_id), board_id=int(board_id))
    db.session.add(assignment)
    db.session.commit()

    flash(f'Poster placed at {board.code}', 'success')
    return redirect(url_for('poster_views.posters_page'))


# ── Remove assignment ─────────────────────────────────────────────

@poster_views.route('/posters/unassign/<int:assignment_id>', methods=['POST'])
def unassign_poster(assignment_id):
    assignment = PosterAssignment.query.get_or_404(assignment_id)
    board = assignment.board
    # Reset board size and color
    board.cell_width = 1
    board.cell_height = 1
    board.color = board.track.color if board.track else '#6c757d'
    db.session.delete(assignment)
    db.session.commit()
    flash('Assignment removed', 'success')
    return redirect(url_for('poster_views.posters_page', tab='board'))


# ── JSON API ─────────────────────────────────────────────────────

@poster_views.route('/api/poster-boards', methods=['GET'])
def get_boards_api():
    track_id = request.args.get('track_id')
    query = PosterBoard.query
    if track_id:
        query = query.filter_by(track_id=track_id)
    return jsonify([b.get_json() for b in query.order_by(PosterBoard.code).all()]), 200


@poster_views.route('/api/poster-assignments', methods=['GET'])
def get_assignments_api():
    assignments = PosterAssignment.query.all()
    return jsonify([a.get_json() for a in assignments]), 200


# ── Zone paint (bulk update track/color for a list of board codes) ──────────

@poster_views.route('/posters/paint-zone', methods=['POST'])
def paint_zone():
    """Assign a track (and its color) to a list of board codes.
    Expects JSON body: { "codes": ["A-1","A-2",...], "track_id": 2 }
    """
    data = request.get_json(silent=True)
    if not data or 'codes' not in data or 'track_id' not in data:
        return jsonify({'error': 'Missing codes or track_id'}), 400

    track = Track.query.get(data['track_id'])
    if not track:
        return jsonify({'error': 'Track not found'}), 404

    codes = data['codes']
    if not isinstance(codes, list) or len(codes) == 0:
        return jsonify({'error': 'codes must be a non-empty list'}), 400

    updated = []
    for code in codes:
        board = PosterBoard.query.filter_by(code=code).first()
        if board:
            board.track_id = track.id
            board.color = track.color
            updated.append(code)

    db.session.commit()
    return jsonify({'updated': updated, 'track_id': track.id, 'color': track.color}), 200
