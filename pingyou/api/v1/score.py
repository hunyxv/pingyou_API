import datetime

from flask import request
from flask_jwt import jwt_required
from flask_restful import reqparse

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import User, Score, Permission
from pingyou.common import util, redis_handle

parser = reqparse.RequestParser()


@api.route('/api/v1/score/', endpoint='score_all')
@api.route('/api/v1/score/<string:id>', endpoint='score')
class ScoreAPI(BaseAPI):
    @jwt_required()
    def get(self, id=None):
        me = get_current_user()
        if not id:
            user_list = User.objects(department=me.department, _class=me._class)
            score_list = Score.objects(student__in=user_list)
            if not score_list():
                score_list=self.post(user_list)

            data = [item.api_response() for item in score_list]
            return util.api_response(data=data)

        score = Score.get_by_id(id=id)
        return util.api_response(data=score.api_response())

    @permission_filter(0x0f)
    def post(self, user_list):
        if user_list:
            month = [8, 9, 10, 11, 12]
            score_list = []
            for user in user_list:
                term=abs((datetime.date.today().year - user.enrollment_date.year) * 2 +
                 [1 if datetime.date.today().month in month else 0][0] - 1)
                score = Score(
                    student=user,
                    term=term
                )
                score.save()
                score_list.append(score)
            return score_list
        return util.api_response()

    @jwt_required()
    @permission_filter(0x0f)
    def put(self,id=None):
        if not id:
            raise ValueError('Id is not find!')

        data = request.get_json()
        score = Score.get_by_id(id=id)

        score.update(data)
        return util.api_response(data={'msg':"success"})
