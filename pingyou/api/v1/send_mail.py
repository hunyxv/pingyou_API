import datetime

from flask import request
from flask_jwt import JWTError, jwt_required

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.jwt_config import jwt
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import User, Role,Department
from pingyou.common import util, send_email, redis_handle



@api.route('/api/v1/sendemail')
class sendEmailAPI(BaseAPI):
    @jwt_required()
    def post(self):
        data = request.get_json()

        email = data.get('email')
        user = get_current_user()

        code = util.generate_code(user)
        if email == user.email:
            send_email.send_email(email,'重置密码', {'username': user.username, 'code': code})