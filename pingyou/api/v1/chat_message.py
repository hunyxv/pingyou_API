import datetime

from flask import request
from flask_jwt import jwt_required
from flask_restful import reqparse

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import ProjectDetail, ChatMessages
from pingyou.common import util, redis_handle

parser = reqparse.RequestParser()


@api.route('/api/v1/messages', endpoint='message')
class ChatMessageAPI(BaseAPI):
    @jwt_required()
    @permission_filter(0x33)
    def get(self):
        parser.add_argument('pdid', type=str, default=None)

        args = parser.parse_args()
        pdid = args.get('pdid')
        if not pdid:
            raise ValueError('project-detail id not find!')

        project_detail = ProjectDetail.get_by_id(id=pdid)

        messages_list = ChatMessages.objects(project_detail=project_detail)

        data = [item.api_response() for item in messages_list]

        return util.api_response(data=data)

    @jwt_required()
    @permission_filter(0x0f)
    def post(self):
        data = request.get_json()

        pdid = data['pdid']
        messages = data['messages']

        if not pdid:
            raise ValueError('project-detail id not find!')

        project_detail = ProjectDetail.get_by_id(id = pdid)

        for message in messages:
            chat_message = ChatMessages(
                project_detail=project_detail,
                name=message['name'],
                message=message['message']
            )
            chat_message.save()

        return util.api_response(data={'msg': 'success'})