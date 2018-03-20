from pingyou import db
from pingyou.models.base_model import BaseModel


class Score(db.Document, BaseModel):
    student_id = db.IntField(required=True)
    term = db.IntField(choices=[1, 2, 3, 4, 5, 6, 7, 8])
    guake = db.BooleanField(default=False)
    jiguo = db.BooleanField(default=False)

    meta = {  # 'db_alias': 'pingyou',  # 在config 的数据库配置中没有配置数据库名时设置
        'indexes': ['student_id', 'term'],
        'collection': 'score'
    }