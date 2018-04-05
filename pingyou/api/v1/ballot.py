import datetime

from flask import request
from flask_jwt import jwt_required
from flask_restful import reqparse

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user
from pingyou.models import Ballot, ProjectDetail, Score, Permission
from pingyou.common import util, redis_handle

parser = reqparse.RequestParser()


@api.route('/api/v1/ballot', endpoint='ballot')
@api.route('/api/v1/ballot/<string:id>', endpoint='ballot_detail')
class BallotAPI(BaseAPI):
    @jwt_required()
    def get(self, id=None):
        me = get_current_user()

        if not id:
            parser.add_argument('pdid', type=str, default=None)

            args = parser.parse_args()
            pdid = args.get('pdid')
            if not pdid:
                raise ValueError('Id is not found!')
            project_detail = ProjectDetail.get_by_id(id=pdid)
            ballot_list = Ballot.objects(project_detail=project_detail, flag=True).order_by('number')
            if me.role.permissions >= 0x33:
                data = [item.api_response() for item in ballot_list]
            else:
                data = [item.api_base_response() for item in ballot_list]
            return util.api_response(data=data)

        ballot = Ballot.get_by_id(id=id)
        if me.role.permissions >= 0x33:
            return util.api_response(data=ballot.api_response())

        return util.api_response(data=ballot.api_base_response())

    @jwt_required()
    def post(self):
        data = request.get_json()
        project_detail_id = data['pdid']

        project_detail = ProjectDetail.get_by_id(id=project_detail_id)
        me = get_current_user()
        # 有申请投票的权力 & 项目没过期 & 项目状态正在投票中
        if me.can(Permission.APPLY_PROJECT) and project_detail.project_exp and project_detail.status == 0:
            if not me.s_id in project_detail.participants:
                month = [8, 9, 10, 11, 12]
                term = ((datetime.date.today().year - me.enrollment_date.year) * 2 +
                        [1 if datetime.date.today().month in month else 0][0])
                score = Score.objects(student=me, term=term-1).first()

                # 上学期没有 挂科和记过 的记录
                if not score.guake and not score.jiguo:
                    project_detail.participants.append(me.s_id)
                    project_detail.save()
                    ballot = Ballot(project_detail=project_detail, people=me)
                    ballot.save()
                    return util.api_response(data={'msg': "success"})
                return util.api_response(data={'msg': "You can't apply for it "})
            return util.api_response(data={'msg': "you already apply for it"})
        return util.api_response(data={'msg': "You can't apply for it "})

    @jwt_required()
    def put(self, id=None):
        if not id:
            raise ValueError('Id is not found!')

        ballot = Ballot.get_by_id(id=id)
        if not ballot.flag:
            return util.api_response({'msg': 'He already cancelled the application.'})
        if ballot.project_detail.status != 1:
            return util.api_response({'msg': 'The ballot has not started or is over!'})
        me = get_current_user()
        if me.s_id not in ballot.ballot_people:
            if not redis_handle.save_hash(key=ballot.project_detail.id, field=me.s_id):
                return util.api_response({'msg': 'no times'})
            ballot.ballot_people.append(me.s_id)
            ballot.number += 1
            ballot.save()
            return util.api_response({'msg': 'success'})
        return util.api_response({'msg': '已经对 %s 投过票！' % ballot.people.name})

    @jwt_required()
    def delete(self, id):
        if not id:
            raise ValueError('Id is not found!')

        ballot = Ballot.get_by_id(id=id)
        me = get_current_user()
        if ballot.people == me:
            ballot.flag = False
            return util.api_response({'msg': 'success'})
        return util.api_response({'msg': 'failure'})