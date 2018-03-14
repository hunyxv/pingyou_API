from flask import jsonify
from pingyou import db
from pingyou.models.base_model import BaseModel

class_name = ['一班', '二班', '三班', '四班', '五班', '六班', '七班', '八班', '九班']

class _Class(BaseModel, db.Document):
    name = db.StringField(required=True, unquire=True, max_length=50)

    meta = {  # 'db_alias': 'pingyou',
        'indexes': ['name'],
        'collection': 'class'}

    def api_response(self):
        return jsonify({
            'id': str(self.id),
            'name': self.name,
        })

    def __repr__(self):
        return '<Class %r>' % self.name
