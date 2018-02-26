from flask_script import Manager

from pingyou import app, api
from pingyou.api import v1

manager = Manager(app)

if __name__ == '__main__':
    app.run()
