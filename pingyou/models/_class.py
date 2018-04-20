from flask import jsonify
from pingyou import db
from pingyou.models.base_model import BaseModel

class_name = ['<无>','一班', '二班', '三班', '四班', '五班', '六班', '七班', '八班', '九班']

class _Class(BaseModel, db.Document):
    num = db.IntField()
    name = db.StringField(required=True, unquire=True, max_length=50)

    meta = {  # 'db_alias': 'pingyou',
        'indexes': ['name'],
        'collection': 'class'}

    def __init__(self, **kwargs):
        super(_Class, self).__init__(**kwargs)

    # @classmethod
    # def test(self):
    #     list = self.objects()
    #     for l in list:
    #         l.num = class_name.index(l.name)
    #         l.save()

    @classmethod
    def query(cls, n):
        if n == 0:
            n = 1
        _class = cls.objects(name = class_name[n]).first()
        return _class

    def api_response(self):
        return {
            'id': str(self.id),
            'name': self.name,
        }

    def __repr__(self):
        return '<Class %r>' % self.name
