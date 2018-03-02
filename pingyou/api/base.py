import traceback
from flask_restful import Resource
from flask_restful.utils import cors
from flask_jwt import JWT, JWTError
from flask_restful import Api
from werkzeug.exceptions import HTTPException

from pingyou.common import util


class BaseAPI(Resource):
    allow_headers = ['Content-Type',
                     'Access-Control-Allow-Headers',
                     'Authorization',
                     ' X-Requested-With', ]

    @cors.crossdomain(origin='*', headers=allow_headers)
    def options(self, id=None):
        return {'Allow': 'True'}


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
