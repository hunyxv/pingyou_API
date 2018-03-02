import datetime

from flask import request, current_app
from flask_jwt import JWTError, jwt_required
from flask_restful import reqparse, inputs

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.jwt_config import jwt
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import User, Role
from pingyou.common import util

parser = reqparse.RequestParser()
Administrator = Role.objects(name='Administrator').first()
Counselor = Role.objects(name='Counselor').first()
Monitor = Role.objects(name='Monitor').first()


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
            if identity.role.permissions >= 0x33 or identity.enrollment_date + \
                    datetime.timedelta(days=365 * 4) > datetime.datetime.today():
                access_token = jwt.jwt_encode_callback(identity)
                return jwt.auth_response_callback(access_token, identity)
            identity.confirmed = False
            identity.save()
        else:
            raise JWTError('Bad Request', 'Invalid credentials')


@api.route('/api/v1/user', endpoint='user_add')
@api.route('/api/v1/user/<string:id>')
class UserAPI(BaseAPI):
    @jwt_required()
    def get(self, id=None):
        current_user = get_current_user()

        if id == 'me':
            return util.api_response(current_user.api_response())
        elif id:
            user = User.get_by_id(id=id)
            if current_user.role.permissions >= 0x33:
                return util.api_response(user.api_response())
            return util.api_response(user.api_base_response())
        else:
            if current_user.role.permissions == 0xff:
                user_list = User.objects().order_by('sid').order_by('s_id')
                data = [item.api_response() for item in user_list]
                return util.api_response(data=data)
            elif current_user.role.permissions == 0x33:
                user_list = User.objects(department=current_user.department).order_by('s_id')
                data = [item.api_response() for item in user_list]
                return util.api_response(data=data)
            else:
                user_list = User.objects(_class=current_user._class).order_by('s_id')
                data = [item.api_response() for item in user_list]
                return util.api_response(data=data)

    @jwt_required()
    @permission_filter([Administrator, Counselor])
    def post(self):
        current_user = get_current_user()

        data = request.get_json()
        # username = data['username'].strip()
        password = data['password'].strip()
        name = data.get('name', '请填写')             # name  创建辅导员用户必须传递
        s_id = data['s_id']
        department = current_user.department
        _class = data['_class']
        if current_user.role == Administrator:
            department = data['department']
            _class = current_user._class

        user = User(
            name=name,
            s_id=s_id,
            department=department,
            _class=_class
        )
        user.password = password
        user.save()

        return util.api_response(user.api_response())


    @jwt_required()
    def put(self):
        pass

    @jwt_required()
    def delete(self):
        pass