import time
import datetime

from flask import jsonify

from pingyou import db
from pingyou.models.base_model import BaseModel
from pingyou.models import User,Project
from pingyou.common import redis_handle


class ProjectDetail(BaseModel, db.Document):
    name = db.StringField(required=True)
    project = db.ReferenceField('Project', required=True)
    department = db.ReferenceField('Department', required=True)
    _class = db.ReferenceField('_Class', required=True)
    counselor = db.ReferenceField('User', required=True)
    places = db.IntField(required=True)      # 名额
    participants = db.ListField(default=[])  # 申请人列表 存放 s_id
    status = db.IntField(default=0)          # 0：投票未开始 1：开始投票 2：这个项目结束 3: 删除或作废
    result = db.ListField(default=[])        # 成功的人 列表

    exp = db.IntField(default=7)
    create_date = db.DateTimeField(default=datetime.datetime.now())

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['name'],
        'collection': 'project_detail'
    }

    def __init__(self, **kwargs):
        super(ProjectDetail, self).__init__(**kwargs)

    def initialize(self, num):
        self.status = 1
        self.save()
        redis_handle.initialize(key=self.id, exp=self.exp)
        user_list = User.objects(department=self.department, confirmed=True)
        for user in user_list:
            redis_handle.save_hash(key=self.id, field=user.id, value=num)

    def filter(self):
        if self.create_date + datetime.timedelta(days=365*2) > datetime.datetime.today():
            return True
        self.status = 3
        self.save()
        return False

    def project_exp(self):
        exp_date = self.create_date + datetime.timedelta(days=self.exp)
        today = datetime.datetime.today()
        if self.status == 2:
            return False
        if today > exp_date:
            self.status = 2
            self.save()
            return False
        return True

    def update(self, data):

        if 'name' in data:
            self.name = data['name']
        if 'department_id' in data:
            self.department = data['department_id']
        if 'project_id' in data:
            self.project = Project.get_by_id(id=data['project_id'])
        if 'place' in data:
            self.places = data['place']
        if 'exp' in data:
            self.places = data['exp']

        self.save()

    def api_response(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'project': {
                'id': str(self.project.id),
                'name': self.project.name
            },
            'department': {
                'id': str(self.department.id),
                'name':self.department.name
            },
            'class': {
                'id': str(self._class.id),
                'name': self._class.name
            },
            'counselor': self.counselor.name,
            'places': self.places,
            'expiration': self.exp,
            'create_date': time.mktime(self.create_date.timetuple()),
            'status': self.status,
            'result': self.result
        }

    def __repr__(self):
        return '<Project Detail %r>' % self.name
