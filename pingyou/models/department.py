from pingyou import db
from pingyou.models.base_model import BaseModel


class Department(BaseModel, db.Document):
    num = db.IntField()
    up_one_level = db.ReferenceField('Department')
    name = db.StringField(required=True, max_length=50)

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['name'],
        'collection': 'department'}

    def api_response(self):
        return {
            'id': str(self.id),
            'name': self.name,
        }

    @classmethod
    def get_by_code(cls, code):
        return cls.objects().get(code=code)

    def __repr__(self):
        return '<Department %r>' % self.name
