from pingyou import db
from pingyou.models.base_model import BaseModel


class Score(db.Document, BaseModel):
    sutdent_id = db.IntField(required=True)
    term = db.IntField(choices=[1, 2, 3, 4, 5, 6, 7, 8])
    subject = db.StringField(required=True)
    guake = db.BooleanField(default=False)
    jiguo = db.BooleanField(default=False)
