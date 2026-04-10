from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
from App.models.user import User
from App.database import db

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


# --- Page routes ---

@auth_views.route('/login', methods=['GET'])
def login_page():
    return render_template('base.html')


@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        flash('Invalid email or password')
        return redirect(url_for('auth_views.login_page'))

    from App.controllers.auth_controller import _create_token
    token = _create_token(user)
    flash('Login successful!')
    response = redirect(url_for('index_views.index_page'))
    set_access_cookies(response, token)
    return response


@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(url_for('auth_views.login_page'))
    flash('Logged out!')
    unset_jwt_cookies(response)
    return response


# --- API routes ---

@auth_views.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    required = ("first_name", "last_name", "email", "password", "role")
    if not all(k in data for k in required):
        return jsonify({"error": f"Missing fields. Required: {list(required)}"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        password=data["password"],
        role=data["role"]
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created", "user": user.get_json()}), 201


@auth_views.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    user.logged_in = True
    db.session.commit()

    return jsonify({"message": "Login successful", "user": user.get_json()}), 200


@auth_views.route('/api/logout', methods=['POST'])
@jwt_required()
def api_logout():
    response = jsonify({"message": "Logged out"})
    unset_jwt_cookies(response)
    return response


@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify():
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }), 200
