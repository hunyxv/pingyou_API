from pingyou import db
from pingyou.models.base_model import BaseModel

class ChatMessages(BaseModel, db.Document):
    project_detail = db.ReferenceField('ProjectDetail', required=True)
    name = db.StringField(required=True)
    message = db.StringField(required=True)

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['project_detail'],
        'collection': 'chat_messages'
    }

    def api_response(self):
        return {
            'id': str(self.id),
            'project_detail': {
                'id':str(self.project_detail.id),
                'name': self.project_detail.name
            },
            'name': self.name,
            'message': self.message
        }

    def __repr__(self):
        return '<Chat Message %r>' % self.name