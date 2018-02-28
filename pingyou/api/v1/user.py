from flask import request
from flask_jwt import JWTError

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.jwt_config import jwt


@api.route('/api/v1/login', endpoint='login')
class LoginAPI(BaseAPI):
    def post(self):
        data = request.get_json()
        username_sid = data.get('username_sid', None)
        password = data.get('password', None)
        criterion = [username_sid, password, len(data) == 2]

        if not all(criterion):
            raise JWTError('Bad Request', 'Invalid credentials')

        identity = jwt.authentication_callback(username_sid, password)

        if identity and identity.confirmed:
            access_token = jwt.jwt_encode_callback(identity)
            return jwt.auth_response_callback(access_token, identity)
        else:
            raise JWTError('Bad Request', 'Invalid credentials')
