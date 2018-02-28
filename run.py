from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from pingyou import app, api, db
from pingyou.api import v1
from pingyou.models import User, Role

manager = Manager(app)
migrate = Migrate(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
