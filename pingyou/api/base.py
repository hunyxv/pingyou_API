from flask_restful import Resource
from flask_restful.utils import cors


class BaseAPI(Resource):
    allow_headers = ['Content-Type',
                     'Access-Control-Allow-Headers',
                     'Authorization',
                     ' X-Requested-With', ]

    @cors.crossdomain(origin='*', headers=allow_headers)
    def options(self, id=None):
        return {'Allow': 'True'}
