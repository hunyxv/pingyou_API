from flask import jsonify
from pingyou import db
from pingyou.models.base_model import BaseModel


class Project(BaseModel, db.Document):
    name = db.StringField(required=True)

    meta = {'db_alias': 'pingyou',
            'indexes': ['name'],
            'collection': 'project'
            }

    def api_response(self):
        return jsonify({
            'id': str(self.id),
            'name': self.name,
        })

    def __repr__(self):
        return '<Project %r>' % self.name