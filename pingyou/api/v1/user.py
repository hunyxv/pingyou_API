from flask import request

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.jwt_config import jwt

@api.route('/api/v1/login')
class LoginAPI(BaseAPI):
    def post(self):
        return 'hello'