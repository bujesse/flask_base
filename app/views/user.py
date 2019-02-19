from flask import (
    render_template,
    Blueprint,
    request,
    flash,
    redirect,
    url_for,
    )
from flask_login import login_user, logout_user, current_user

from app.services.auth import (
    AuthenticationError,
    InvalidCredentialsError,
    AccountError,
    authenticate_user,
    )

blueprint = Blueprint('user', __name__)


@blueprint.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index.index'))

    return render_template(
        'user/login.jinja.html'
    )


@blueprint.route('/login', methods=['POST'])
def do_login():
    try:
        user = authenticate_user(request.form.get('username'), request.form.get('password'))
        login_user(user, remember=True)
        flash('Welcome back, %s' % (user.first_name,), 'info')
        return redirect(url_for('index.index'))
    except InvalidCredentialsError:
        flash('Invalid username or password', 'error')
    except AccountError as e:
        flash(str(e), 'error')
    except AuthenticationError:
        flash('Unexpected authentication failure', 'error')

    return redirect(url_for('user.login'))


@blueprint.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('user.login'))
