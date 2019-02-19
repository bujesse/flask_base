import logging

from flask import current_app, session

from app.models.user import User
from app.main import login_manager, on_app
from sqlalchemy.orm.exc import NoResultFound


logger = logging.getLogger(__name__)


@on_app
def _attach_perm_session_setup(app):
    @app.before_request
    def _perm_session_setup():
        session.permanent = True
        session.modified = True


@login_manager.user_loader
def _user_loader(uid):
    return User.query.get(uid)


class AuthenticationError(Exception):
    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class AccountError(AuthenticationError):
    pass


def authenticate_user(username, password):
    try:
        user = User.query.filter_by(username=username, password=password).one()
    except NoResultFound:
        raise InvalidCredentialsError("Invalid username or password")

    if not user.enabled:
        raise AccountError("Your account has been disabled")

    return user
