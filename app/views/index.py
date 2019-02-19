from flask import (
    render_template,
    Blueprint,
    Response,
    flash,
    redirect,
    url_for,
    request,
    current_app
)
from flask_login import login_required
import requests

blueprint = Blueprint('index', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template("index.jinja.html")
