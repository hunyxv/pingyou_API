import types
import os

from flask import Flask
from flask_mail import Mail
from flask_mongoengine import MongoEngine

from config import config
from pingyou.api.base import Service

# app.config['JWT_AUTH_URL_RULE'] = None
# app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=14)
app = Flask(__name__)


def api_route(self, *args, **kwargs):
    def wrapper(cls):
        self.add_resource(cls, *args, **kwargs)
        return cls

    return wrapper


# 进行配置
config_name = os.getenv('FLASK_CONFIG') or 'default'
app.config.from_object(config[config_name])
config[config_name].init_app(app)
mail = Mail(app)
db = MongoEngine(app)
api = Service(app)
api.route = types.MethodType(api_route, api)
