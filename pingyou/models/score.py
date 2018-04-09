from pingyou import db
from pingyou.models.base_model import BaseModel


class Score(db.Document, BaseModel):
    student = db.ReferenceField('User')
    term = db.IntField(choices=[1, 2, 3, 4, 5, 6, 7, 8])
    score = db.FloatField()
    guake = db.BooleanField(default=False)
    jiguo = db.BooleanField(default=False)

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['student', 'term'],
        'collection': 'score'
    }

    def update(self, data):
        if 'guake' in data:
            self.guake = data['guake']
        if 'jiguo' in data:
            self.jiguo = data['jiguo']

        self.save()

    def api_response(self):
        return {
            'id': str(self.id),
            's_id': self.student.s_id,
            'name': self.student.name,
            'term': self.term,
            'score': self.score,
            'guake': self.guake,
            'jiguo': self.jiguo
        }