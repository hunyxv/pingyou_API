from pingyou import db
from pingyou.models.base_model import BaseModel

class WeChat(db.Document):
    title = db.StringField(required=True)
    img = db.StringField()
    content_url = db.StringField()
    intro = db.StringField()
    date = db.IntField()

    meta = {
        'indexes': ['title', 'date'],
        'collection': 'wechat',
    }

    def update(self,data):
        if 'content_url' in data:
            self.content_url = data['content_url']
        if 'title' in data:
            self.title = data['title']
        if 'img' in data:
            self.img = data['img']
        if 'intro' in data:
            self.intro = data['intro']
        self.save()

    def api_response(self):
        return {
            'title': self.title,
            'img': self.img,
            'content_url':self.content_url,
            'intro': self.intro,
            'date': self.date
        }

    def __repr__(self):
        return '<WeChat %r>' % self.title