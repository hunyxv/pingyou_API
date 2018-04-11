from pingyou import db
from pingyou.models.base_model import BaseModel
from pingyou.models import User


class Ballot(BaseModel, db.Document):
    project_detail = db.ReferenceField('ProjectDetail', required=True)
    people = db.ReferenceField('User', required=True)
    ballot_people = db.ListField(default=[])
    number = db.IntField(default=0)
    integration = db.FloatField(defautl=0)
    flag = db.BooleanField(default=True)

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['project_detail', 'people'],
        'collection': 'ballot'
    }

    def __init__(self, **kwargs):
        super(Ballot, self).__init__(**kwargs)
        if self.project_detail.status >=3:
            self.flag = False
            self.save()


    def update_number(self):
        if self.project_detail.status == 1:
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
            'integration':self.integration,
            'ballot_people': self.ballot_people,
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
            'integration': self.integration,
            'ballot_people': [User.get_by_sid(sid=item).name
                              for item in self.ballot_people],
            'number': self.number
        }

    def __repr__(self):
        return '<Project Detail %r>' % self.people.name