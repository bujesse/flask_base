#! /usr/bin/env python

import logging

from flask_script import Shell
from flask_migrate import Migrate, MigrateCommand

from app.main import create_app as get_app
app = get_app()

from app.main import db, manager


migrate = Migrate(app, db)
logger = logging.getLogger('app')

manager.add_command('db', MigrateCommand)


def make_shell_context():
    return_dict = {
        'app': app,
        'db': db,
        'session': db.session
    }

    def go(obj):
        db.session.add(obj)
        db.session.commit()
    return_dict['go'] = go
    return return_dict


# convenience to have all of the above objects available
manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
