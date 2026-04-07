from App.models import User
from App.database import db


def create_user(first_name, last_name, email, password, role="REGULAR_USER"):
    existing_user = User.query.filter_by(email=email).first()
    
    if existing_user:
        return None  

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return new_user


def get_user(user_id):
    return User.query.get(user_id)


def get_all_users():
    return User.query.all()


def get_all_users_json():
    users = User.query.all()
    return [user.get_json() for user in users]


def user_login(email, password):
    user = User.query.filter_by(email=email).first()

    if user and user.login(password):
        return user

    return None


def user_logout(user_id):
    user = User.query.get(user_id)

    if user:
        user.logout()
        return True

    return False