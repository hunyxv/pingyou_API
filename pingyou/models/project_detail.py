import datetime
from pingyou import db
from pingyou.models.base_model import BaseModel


class Project_detail(BaseModel, db.Document):
    name = db.StringField(required=True)
    project = db.ReferenceField('Project', required=True)
    department = db.StringField(required=True)
    _class = db.StringField(required=True)
    counselor = db.ReferenceField('User')
    places = db.IntField(required=True)
    status = db.BooleanField(default=False)
    result = db.DictField()
    create_date = db.DateTimeField(default=datetime.datetime.now())
    exp = db.IntField(default=7)

    meta = {'db_alias': 'pingyou',
            'indexes': ['name'],
            'collection': 'project'
            }
