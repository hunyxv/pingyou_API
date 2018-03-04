import datetime

from flask import request, current_app
from flask_jwt import JWTError, jwt_required
from flask_restful import reqparse, inputs

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.jwt_config import jwt
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import User, Role, Permission
from pingyou.common import util

parser = reqparse.RequestParser()


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


@api.route('/api/v1/code', endpoint='code')
class CodeApi:
    @jwt_required()
    def get(self):
        current_user = get_current_user()
        util.generate_code(current_user)


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
    @permission_filter(0x33)
    def post(self):
        current_user = get_current_user()

        data = request.get_json()
        # username = data['username'].strip()
        password = data['password'].strip()
        name = data.get('name', '请填写')  # name  创建辅导员用户必须传递
        s_id = data['s_id']
        department = current_user.department
        _class = data['_class']
        if current_user.can(Permission.ADMINSTER):
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
    def put(self, id=None):
        if not id:
            raise ValueError('Id is not found!')
        data = request.get_json()
        current_user = get_current_user()

        if id == 'me':
            if 'password' in data and 'code' in data:
                if util.verify_code(current_user, data['code']):
                    current_user.password = data['password']
                    return util.api_response({'success': True})
                return util.api_response({'success': False})

            data.pop('name', None)
            data.pop('confirmed', None)
            current_user.update_info(**data)
            return util.api_response(current_user.api_response())

        user = User.get_by_id(id=id)
        if (current_user.role.permissions == 0x0f and
                current_user.role.permissions > user.role.permissions):   # 班长
            user.update(name=data['name'])
            return util.api_response(user.api_response())
        elif current_user.role.permissions > user.role.permissions:
            user.update(**data)
            return util.api_response(user.api_response())
        else:
            user.update(**data)
            return util.api_response(user.api_response())

    @jwt_required()
    @permission_filter(0x33)
    def delete(self, id=None):
        if id is None:
            raise ValueError('Id not found')
        user = User.objects.get(id=id)
        current_user = get_current_user()
        if current_user.role.permissions > user:
            user.confirmed = False
            user.save()
            return util.api_response(data={'SUCCESS': True})
        return util.api_response(data={'SUCCESS': False})