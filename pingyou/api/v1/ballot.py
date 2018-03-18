import datetime

from flask import request
from flask_jwt import JWTError, jwt_required
from flask_restful import reqparse, inputs

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.jwt_config import jwt
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import Ballot, User, ProjectDetail
from pingyou.common import util, send_email, redis_handle

parser = reqparse.RequestParser()


@api.route('/api/v1/ballot', endpoint='ballot')
class BallotAPI(BaseAPI):
    def get(self, id=None):
        if not id:
            raise ValueError('Id is not found!')

        user = get_current_user()

        ballot = Ballot.get_by_id(id=id)
        if user.role.permissions >= 0x33:
            return util.api_response(data=ballot.api_response())

        return util.api_response(data=ballot.api_base_response())


    @jwt_required()
    def post(self):
        data = request.get_json()
        project_detail_id = data['pdid']
        user_id = data['uid']

        project_detail = ProjectDetail.get_by_id(id=project_detail_id)
        user = User.get_by_id(id=user_id)
        if (project_detail and user and
                not Ballot.objects(project_detail=project_detail, people=user)):
            ballot = Ballot(project_detail=project_detail, people=user)

    @jwt_required()
    def put(self, id=None):
        if not id:
            raise ValueError('Id is not found!')

        ballot = Ballot.get_by_id(id=id)
        user = get_current_user()
        if user.s_id not in ballot.ballot_people:
            if not redis_handle.save_hash(ballot.project_detail.id, user.id):
                return util.api_response({'msg': 'no times'})
            ballot.ballot_people.append(user.s_id)
            ballot.number += 1
            ballot.save()
            return util.api_response({'msg': 'success'})
        return util.api_response({'msg': '已经对 %s 投过票！' % ballot.people.name})
