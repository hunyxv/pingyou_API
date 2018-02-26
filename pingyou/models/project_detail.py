import time
import datetime

from flask import jsonify

from pingyou import db
from pingyou.models.base_model import BaseModel


class Project_detail(BaseModel, db.Document):
    name = db.StringField(required=True)
    project = db.ReferenceField('Project', required=True)
    department = db.ReferenceField('Department',required=True)
    _class = db.ReferenceField('_Class', required=True)
    counselor = db.ReferenceField('User', required=True)
    places = db.IntField(required=True)
    status = db.BooleanField(default=False)
    result = db.DictField()

    exp = db.IntField(default=7)
    create_date = db.DateTimeField(default=datetime.datetime.now())

    meta = {'db_alias': 'pingyou',
            'indexes': ['name'],
            'collection': 'project'
            }

    def api_response(self):
        data = {
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
        return jsonify({'data': data})

    def __repr__(self):
        return '<Project Detail %r>' % self.name