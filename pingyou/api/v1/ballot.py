import datetime

from flask import request
from flask_jwt import JWTError, jwt_required
from flask_restful import reqparse, inputs

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import Ballot, ProjectDetail, Score, Permission
from pingyou.common import util, redis_handle

parser = reqparse.RequestParser()


@api.route('/api/v1/ballot', endpoint='ballot')
@api.route('/api/v1/ballot/<string:id>', endpoint='ballot_detail')
class BallotAPI(BaseAPI):
    @jwt_required()
    def get(self, id=None):
        if not id:
            parser.add_argument('pdid', type=str, default=None)

            args = parser.parse_args()
            pdid = args.get('pdid')
            if not pdid:
                raise ValueError('Id is not found!')
            project_detail = ProjectDetail.get_by_id(id=pdid)
            ballot_list = Ballot.objects(project_detail=project_detail)
            data = [item.api_base_response() for item in ballot_list]
            return util.api_response(data=data)

        me = get_current_user()

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

        if project_detail and me.can(Permission.APPLY_PROJECT):
            if not Ballot.objects(project_detail=project_detail, people=me).first():
                month = [8, 9, 10, 11, 12]
                term = ((datetime.date.today().year - me.enrollment_date.year) * 2 +
                        [1 if datetime.date.today().year in month else 0][0])
                source = Score.objects(student_id=me.s_id, term=term-1).first()
                if not source.guake and not source.jiguo:
                    ballot = Ballot(project_detail=project_detail, people=me)
                    ballot.save()
                    return util.api_response(data=ballot.api_base_response())
                return util.api_response(data={'msg': "You can't apply for it "})

    @jwt_required()
    def put(self, id=None):
        if not id:
            raise ValueError('Id is not found!')

        ballot = Ballot.get_by_id(id=id)
        if not ballot.flag:
            return util.api_response({'msg': 'He already cancelled the application.'})
        me = get_current_user()
        if me.s_id not in ballot.ballot_people:
            if not redis_handle.save_hash(key=ballot.project_detail.id, field=me.id):
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