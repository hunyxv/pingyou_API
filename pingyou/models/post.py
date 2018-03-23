from pingyou import db
from pingyou.models.base_model import BaseModel
from pingyou.models import User


class Post(BaseModel, db.Document):
    pass