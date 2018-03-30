from pingyou import db
from pingyou.models.base_model import BaseModel


class News(BaseModel, db.Document):
    department = db.ReferenceField('Department')
    _class = db.ReferenceField('_Class')
    author = db.ReferenceField('User')
    news = db.StringField(max_length=256)

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['department', '_class', 'author'],
        'collection': 'news'}

    def api_response(self):
        return {
            'id': str(self.id),
            'deparment': self.department.name,
            'class': self._class.name,
            'author': self.author.name,
            'news': self.news
        }

    def __repr__(self):
        return '<Department %r>' % self.news