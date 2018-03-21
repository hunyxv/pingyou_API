from pingyou import db
from pingyou.models.base_model import BaseModel
from pingyou.models import User
from pingyou.common.redis_handle import save_hash


class Ballot(BaseModel, db.Document):
    project_detail = db.ReferenceField('ProjectDetail', required=True)
    people = db.ReferenceField('User', required=True)
    ballot_people = db.ListField(default=[])
    number = db.IntField(default=0)
    flag = db.BooleanField(default=True)

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['project_detail', 'people'],
        'collection': 'ballot'
    }

    def __init__(self, **kwargs):
        super(Ballot, self).__init__(**kwargs)


    def update_number(self):
        if not self.project_detail.status:
            self.number += 1
            self.save()

    def api_base_response(self):
        return {
            'id': str(self.id),
            'people': {
                'id': str(self.people.id),
                'name': self.people.name
            },
            'project_detail': {
                'id': str(self.project_detail.id),
                'name': self.project_detail.name
            },
            'ballot_people': [],
            'number': self.number
        }

    def api_response(self):
        return {
            'id': str(self.id),
            'people': {
                'id': str(self.people.id),
                'name': self.people.name
            },
            'project_detail': {
                'id': str(self.project_detail.id),
                'name': self.project_detail.name
            },
            'ballot_people': [User.get_by_sid(sid=item).name
                              for item in self.ballot_people],
            'number': self.number
        }

    def __repr__(self):
        return '<Project Detail %r>' % self.people.name