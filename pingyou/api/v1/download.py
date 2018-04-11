import os
from flask import request, send_file
from flask_jwt import jwt_required
from flask_restful import reqparse

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import User, Score
from pingyou.common import util, redis_handle

parser = reqparse.RequestParser()


@api.route('/api/v1/download', endpoint="download")
class DownLoadAPI(BaseAPI):
    def get(self):
        parser.add_argument('filename', type=str)
        args = parser.parse_args()

        filename = args.get('filename')
        print(os.getcwd()+ '/files/' + filename)

        return send_file(os.getcwd()+ '/files/' + filename,
                         attachment_filename=filename)

