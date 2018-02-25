import datetime
import traceback
import types

from flask import Flask
from flask_jwt import JWT, JWTError
from flask_restful import Api
from flask_mongoengine import MongoEngine
from werkzeug.exceptions import HTTPException

from config import config
from pingyou.common import util


# app.config['JWT_AUTH_URL_RULE'] = None
# app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=14)


class Service(Api):

    def handle_error(self, e):
        print(traceback.print_exc())
        if isinstance(e, HTTPException):
            return super(Service, self).handle_error(e)
        elif isinstance(e, JWTError):
            data = {'msg': str(e.description)}
            return self.make_response(*util.api_response(data, e.status_code))
        else:
            data = {'msg': str(e)}
            return self.make_response(*util.api_response(data, 500))


db = MongoEngine()
api = Service()


def api_route(self, *args, **kwargs):
    def wrapper(cls):
        self.add_resource(cls, *args, **kwargs)
        return cls

    return wrapper


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    api.init_app(app)

    api.route = types.MethodType(api_route, api)

    return app, api
