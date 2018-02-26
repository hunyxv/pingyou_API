from flask import jsonify
from pingyou import db
from pingyou.models.base_model import BaseModel


class _Class(BaseModel, db.Document):
    name = db.StringField()

    meta = {'db_alias': 'pingyou',
            'indexes': ['name'],
            'collection': '_class'}

    def api_response(self):
        return jsonify({
            'id': str(self.id),
            'name': self.name,
        })

    def __repr__(self):
        return '<Class %r>' % self.name
