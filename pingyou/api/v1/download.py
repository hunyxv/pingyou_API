import os
from flask import make_response, send_from_directory
from flask_jwt import jwt_required
from flask_restful import reqparse

from pingyou import api
from pingyou.api.base import BaseAPI

parser = reqparse.RequestParser()


@api.route('/api/v1/download', endpoint="download")
class DownLoadAPI(BaseAPI):
    def get(self):
        parser.add_argument('filename', type=str)
        args = parser.parse_args()

        filename = args.get('filename')
        print(os.getcwd()+ '/files/' + filename)

        response = send_from_directory(os.getcwd()+ '/files/',filename, as_attachment=True)
        response.headers["Content-Disposition"] = "attachment; filename={}".format(
            os.getcwd() + '/files/' + filename.encode().decode('latin-1'))
        return response

