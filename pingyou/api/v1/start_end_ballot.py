import datetime

from flask import request
from flask_jwt import jwt_required
from flask_restful import reqparse

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user
from pingyou.models import Ballot, ProjectDetail, Score, Permission, User
from pingyou.common import util, redis_handle

parser = reqparse.RequestParser()


@api.route('/api/v1/start_ballot/<string:id>', endpoint='startballot')
class StartBallot(BaseAPI):
    @jwt_required()
    @jwt_required(0x0f)
    def post(self, id=None):
        if not id:
            raise ValueError('id is not find')

        parser.add_argument('status', type=int, default=None)
        args = parser.parse_args()
        status = args.get('status')
        print(status)
        current_user = get_current_user()
        project_detail = ProjectDetail.get_by_id(id=id)
        project_detail.status = status
        project_detail.save()
        if status == 1:
            ClassStudent = User.objects(
                department=current_user.department,
                _class=current_user._class,
                confirmed=True
            )
            thisClassStudent = [item for item in ClassStudent if item.period == current_user.period]
            # 根据这个项目过期时间 在redis中创建一个hash结构 记录每个用户投票剩余次数
            redis_handle.initialize(key=id, exp=project_detail.exp)
            print('本班人数：', len(thisClassStudent))
            for student in thisClassStudent:
                redis_handle.save_hash(key=id, field=student.s_id, value=project_detail.places)

        return util.api_response(data={'msg': 'success'})


@api.route('/api/v1/end_ballot/<string:id>', endpoint='endballot')
class EndBallot(BaseAPI):
    @jwt_required()
    @jwt_required(0x0f)
    def post(self, id=None):
        if not id:
            raise ValueError('id is not find')

        parser.add_argument('status', type=int, default=None)
        args = parser.parse_args()
        status = args.get('status')

        current_user = get_current_user()
        project_detail = ProjectDetail.get_by_id(id=id)
        project_detail.status = status
        project_detail.save()
        if status == 2:
            ClassStudent = User.objects(
                department=current_user.department,
                _class=current_user._class,
                confirmed=True
            )
            thisClassStudent = [item for item in ClassStudent if item.period == current_user.period]
            # 根据这个项目过期时间 在redis中创建一个hash结构 记录每个用户投票剩余次数
            # redis_handle.initialize(key=id, exp=project_detail.exp)
            print('本班人数：', len(thisClassStudent))
            # for student in thisClassStudent:
                # redis_handle.save_hash(key=id, field=student.s_id, value=project_detail.places)
            month = [8, 9, 10, 11, 12]
            term = abs((datetime.date.today().year - current_user.enrollment_date.year) * 2 +
                       [1 if datetime.date.today().month in month else 0][0] - 1)
            ballotList = Ballot.objects(people__in=thisClassStudent, project_detail=project_detail)
            for ballot in ballotList:
                score = Score.objects(student=ballot.people, term=term-1).first()
                if score:
                    ballot.integration = round(score.score * 0.7 + ballot.number * 0.3, 2)
                    ballot.save()

        return util.api_response(data={'msg': 'success'})
