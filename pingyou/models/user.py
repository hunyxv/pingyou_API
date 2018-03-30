import datetime

import re
from werkzeug.security import generate_password_hash, check_password_hash

from pingyou import db
from pingyou.models.base_model import BaseModel
from pingyou.common import util
from flask import current_app

'''
    匿名              0b00000000      0x00
    用户、其他班干      0b00000111      0x07
    班长、团委          0b00001111     0x0f
    辅导员             0b00110011      0x33
    管理员             0b11111111      0xff
'''


class Permission:
    COMMENT = 0x01  # 评论权限
    LOOKREPORT = 0x02  # 查看报告
    APPLY_PROJECT = 0x04  # 申请项目
    WRITE_ARTICLES = 0x08  # 撰写评选报告
    RELEASE_PROJECT = 0x10  # 发布项目
    AUDITING = 0x20  # 审核项目
    UPDATE_INFO = 0x40
    ADMINSTER = 0xff  # 管理员权限


class Role(db.Document, BaseModel):
    name = db.StringField(uniqe=True)
    default = db.BooleanField(default=False)
    permissions = db.IntField()

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'collection': 'role'
    }

    @staticmethod
    def insert_roles():
        roles = {
            'Student': (Permission.COMMENT |
                        Permission.LOOKREPORT |
                        Permission.APPLY_PROJECT, True),
            'Monitor': (Permission.COMMENT |
                        Permission.LOOKREPORT |
                        Permission.APPLY_PROJECT |
                        Permission.WRITE_ARTICLES, False),
            'Counselor': (Permission.COMMENT |
                          Permission.LOOKREPORT |
                          Permission.RELEASE_PROJECT |
                          Permission.AUDITING |
                          Permission.UPDATE_INFO, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.objects(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            role.save()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(BaseModel, db.Document):
    username = db.StringField(unique=True, max_length=50)
    password_bash = db.StringField()
    role = db.ReferenceField('Role')
    confirmed = db.BooleanField(default=True)
    #is_live = db.BooleanField(default=False)

    name = db.StringField(required=True)
    s_id = db.IntField(required=True, unique=True)
    gender = db.StringField(
        choices=[
            'Male',
            'Female',
            'Secret'],
        default='Secret')
    department = db.ReferenceField('Department', required=True, max_length=50)
    _class = db.ReferenceField('_Class')
    email = db.EmailField()
    qq_num = db.StringField(max_length=10)
    weixin = db.StringField(max_length=50)

    enrollment_date = db.DateTimeField(default=datetime.datetime.today())

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['username', 'name', 's_id'],
        'collection': 'users'
    }

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            # current_app.config['PINGYOU_ADMIN']:
            if self.email == '1035794358@qq.com':
                self.role = Role.objects(permissions=0xff).first()
                self.enrollment_date = datetime.datetime.max
            elif self.s_id < 2000000000:
                self.role = Role.objects(permissions=0x33).first()
                self.enrollment_date = datetime.datetime.max
            if self.role is None:
                self.role = Role.objects(default=True).first()
        if self.username is None:
            self.username = 'XK' + str(self.s_id)
        if (self.role.permissions < 0x33 and
                self.enrollment_date +datetime.timedelta(days=365 * 4)
                < datetime.datetime.today()):
            self.confirmed = False


    def can(self, permissions):
        return self.role is not None and (
            self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINSTER)

    @property
    def password(self):
        raise AttributeError('password is not a readable')

    # 设置密码
    @password.setter
    def password(self, password):
        self.password_bash = generate_password_hash(str(password))

    def update_info(self, **kwargs):
        if 'name' in kwargs:
            self.name = util.clear_str(kwargs['name'])
        if 'username' in kwargs:
            self.username = util.clear_str(kwargs['username'])
        if 'confirmed' in kwargs:
            self.confirmed = kwargs['confirmed']
        if 'role' in kwargs:
            if kwargs['role'] == 0:
                self.role = Role.objects(name='Student').first()
            else:
                self.role = Role.objects(name='Monitor').first()
        if 'gender' in kwargs:
            self.gender = kwargs['gender']
        if 'department' in kwargs:
            self.department = kwargs['department']
        if '_class' in kwargs:
            self._class = kwargs['_class']
        if 'email' in kwargs:
            self.email = kwargs['email']
        if 'qq_num' in kwargs:
            self.qq_num = kwargs['qq_num']
        if 'weixin' in kwargs:
            self.weixin = kwargs['weixin']

        self.save()

    def api_response(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'role': self.role.name,
            #'is_live': self.is_live,
            'name': self.name,
            's_id': self.s_id,
            'confirmed': self.confirmed,
            'gender': self.gender,
            'department': self.department.name,
            'class': self._class.name,
            'email': self.email,
            'qq_num': self.qq_num,
            'weixin': self.weixin,
        }

    def api_base_response(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'role': self.role.name,
            'confirmed': self.confirmed,
            'gender': self.gender,
            'department': self.department.name,
            'class': self._class.name
        }

    @classmethod
    def get_by_username(cls, username):
        user = cls.objects(username=username).first()
        return user if user else None

    @classmethod
    def get_by_sid(cls, sid):
        user = cls.objects(s_id=sid).first()
        return user if user else None

    def verify_password(self, password):
        return check_password_hash(self.password_bash, password)

    # 验证密码
    @classmethod
    def validate_password(cls, username_sid, password):
        user = cls.get_by_username(username_sid)
        if not user:
            user = cls.get_by_sid(username_sid)
        if user and user.verify_password(str(password).encode('utf-8')):
            return user

    def __repr__(self):
        return '<User %r>' % self.username


def authenticate(username_sid, password):
    user = User.validate_password(username_sid, password)
    return user if user else None


def identity(payload):
    return User.objects.get(id=payload['identity'])
