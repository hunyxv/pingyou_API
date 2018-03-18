import time
import datetime

from flask import jsonify

from pingyou import db
from pingyou.models.base_model import BaseModel


class ProjectDetail(BaseModel, db.Document):
    name = db.StringField(required=True)
    project = db.ReferenceField('Project', required=True)
    department = db.ReferenceField('Department', required=True)
    _class = db.ReferenceField('_Class', required=True)
    counselor = db.ReferenceField('User', required=True)
    places = db.IntField(required=True)      # 名额
    participants = db.ListField(default=[])  # 申请人列表 存放 s_id
    status = db.IntField(default=0)          # 0：投票未开始 1：开始投票 2：这个项目结束
    result = db.ListField(default=[])        # 成功的人 列表

    exp = db.IntField(default=7)
    create_date = db.DateTimeField(default=datetime.datetime.now())

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['name'],
        'collection': 'project'
    }

    def api_response(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'project': self.project.name,
            'department': self.department.name,
            'class': self._class.name,
            'counselor': self.counselor.name,
            'places': self.places,
            'expiration': self.exp,
            'create_date': time.mktime(self.create_date.timetuple()),
            'exp_date': time.mktime(
                self.create_date + datetime.timedelta(days=self.exp))
        }

    def __repr__(self):
        return '<Project Detail %r>' % self.name
