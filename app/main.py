from flask import Flask
from flask_script import Manager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from xconfig import get_config


manager = None
apps = []
on_app_callbacks = []
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message = 'You must be logged in to access that page.'
login_manager.login_message_category = 'danger'
login_manager.session_protection = 'strong'


def on_app(callback):
    on_app_callbacks.append(callback)
    for app in apps:
        callback(app)
    return callback


def call_on_app_callbacks(app):
    for cb in on_app_callbacks:
        cb(app)


def create_app(env=None):
    global manager

    app = Flask(__name__)

    # Config stuff
    config = get_config(env)
    app.config.from_object(config)

    # Initialize libs
    login_manager.init_app(app)
    manager = Manager(app)
    db.init_app(app)
    Bootstrap(app)

    # Make custom jinja filters callable from the templates
    from app.lib import jinja_ext
    for ext_name in dir(jinja_ext):
        if not ext_name.startswith('_'):
            ext_fn = getattr(jinja_ext, ext_name)
            if ext_name.startswith('global__'):
                app.jinja_env.globals[ext_name[8:]] = ext_fn() if callable(ext_fn) else ext_fn
            elif callable(ext_fn) and ext_name.startswith('filter__'):
                app.jinja_env.filters[ext_name[8:]] = ext_fn

    # Register views
    from app.views import user, index
    app.register_blueprint(index.blueprint, url_prefix='/')
    app.register_blueprint(user.blueprint, url_prefix='/user')

    call_on_app_callbacks(app)
    apps.append(app)

    return app
