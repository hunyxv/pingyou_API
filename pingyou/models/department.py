from flask import jsonify
from pingyou import db
from pingyou.models.base_model import BaseModel


class Department(BaseModel, db.Document):
    name = db.StringField()

    meta = {'db_alias': 'pingyou',
            'indexes': ['name'],
            'collection': 'department'}

    def api_response(self):
        return jsonify({
            'id': str(self.id),
            'name': self.name,
        })

    @classmethod
    def get_by_code(cls, code):
        return cls.objects().get(code=code)

    def __repr__(self):
        return '<Department %r>' % self.name
