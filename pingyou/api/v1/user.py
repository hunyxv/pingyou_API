import datetime

from flask import request
from flask_jwt import JWTError, jwt_required
from flask_restful import reqparse, inputs

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.jwt_config import jwt
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import User, Role,Department
from pingyou.common import util, send_email, redis_handle


@api.route('/api/v1/login', endpoint='login')
class LoginAPI(BaseAPI):
    def post(self):
        """
        用户登录
        :return:
        """
        data = request.get_json()
        username_sid = data.get('username_sid', None)
        password = data.get('password', None)
        criterion = [username_sid, password, len(data) == 2]

        if not all(criterion):
            raise JWTError('Bad Request', 'Invalid credentials')

        identity = jwt.authentication_callback(username_sid, password)
        if identity and identity.confirmed:
            if identity.role.permissions >= 0x33 or (identity.enrollment_date +
                                                     datetime.timedelta(days=365 * 4) > datetime.datetime.today()):
                access_token = jwt.jwt_encode_callback(identity)
                return jwt.auth_response_callback(access_token, identity)
            identity.confirmed = False
            identity.save()
        else:
            raise JWTError('Bad Request', 'Invalid credentials')


@api.route('/api/v1/code', endpoint='code')
class CodeApi(BaseAPI):
    @jwt_required()
    def get(self):
        """
        重设密码时用来生成验证码 并 通过邮件发给用户
        发送邮件最好用异步方式 暂时没用
        :return: json
        """
        current_user = get_current_user()
        if not redis_handle.exp_time(current_user.id):
            code = util.generate_code(current_user)
            context = {'username': current_user.name, "code": code}
            send_email.send_email(current_user.email, "修改密码", context)
            return util.api_response({'msg': 'success'})


@api.route('/api/v1/user', endpoint='user_add')
@api.route('/api/v1/user/<string:id>', endpoint='user_detail')
class UserAPI(BaseAPI):
    @jwt_required()
    def get(self, id=None):
        """
        获取用户信息
        :param id: str
        :return: json
        """
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
                department_list = Department.objects(up_one_level=current_user.department)
                user_list = User.objects(
                    department__in=department_list).order_by('s_id')
                data = [item.api_response() for item in user_list]
                return util.api_response(data=data)
            else:
                user_list = User.objects(
                    department=current_user.department,
                    _class=current_user._class).order_by('s_id')
                data = [item.api_response() for item in user_list]
                return util.api_response(data=data)

    @jwt_required()
    @permission_filter(0x33)
    def post(self):
        """
        创建用户
        只有辅导员以上级别能创建
        :return:
        """
        # current_user = get_current_user()

        data = request.get_json()
        # username = data['username'].strip()
        password = data['password'].strip()
        name = data.get('name', '请填写')
        s_id = data['s_id']
        department = data['department']
        _class = data['_class']

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
        """
        更新 用户信息 密码
        :param id: str
        :return: json
        """
        if not id:
            raise ValueError('Id is not found!')
        data = request.get_json()
        current_user = get_current_user()

        if id == 'me':
            if 'password' in data and 'code' in data:  # 如果密码 和验证码 在传输的数据里 则是修改密码
                if util.verify_code(current_user, data['code']):
                    current_user.password = data['password']
                    current_user.save()
                    return util.api_response({'msg': 'success'})
                return util.api_response({'msg': 'failure'})
            data.pop('name', None)
            data.pop('department', None)
            data.pop('_class', None)
            data.pop('role', None)
            current_user.update_info(**data)
            return util.api_response(current_user.api_response())

        user = User.get_by_id(id=id)
        if (current_user.role.permissions == 0x0f and
                current_user.department == user.department and
                current_user._class == user._class):  # 班长
            user.update_info(name=data['name'])
            return util.api_response(user.api_response())
        elif current_user.role.permissions > user.role.permissions:
            user.update_info(**data)
            return util.api_response(user.api_response())
        raise Exception("User don't have permissionro change!")

    @jwt_required()
    @permission_filter(0x33)
    def delete(self, id=None):
        """
        删除用户 使用户过期
        只有高级用户更改低级用户
        :param id:
        :return:
        """
        if id is None:
            raise ValueError('Id not found')
        user = User.objects.get(id=id)
        current_user = get_current_user()
        if current_user.role.permissions > user.role.permissions:
            user.confirmed = False
            user.save()
            return util.api_response(data={'msg': 'success'})
        return util.api_response(data={'msg': 'success'})
