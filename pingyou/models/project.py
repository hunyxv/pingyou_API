from pingyou import db
from pingyou.models.base_model import BaseModel


class Project(BaseModel, db.Document):
    name = db.StringField(required=True)

    meta = {'db_alias': 'pingyou',
            'indexes': ['name'],
            'collection': 'project'
            }
