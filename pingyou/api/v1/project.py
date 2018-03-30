from flask import request
from flask_jwt import jwt_required

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import permission_filter
from pingyou.models import Project
from pingyou.common import util


@api.route('/api/v1/project', endpoint='project')
@api.route('/api/v1/project/<string:id>', endpoint='project_del')
class ProjectAPI(BaseAPI):
    def get(self):
        project_list = Project.objects()
        data = [item.api_response() for item in project_list]

        return util.api_response(data=data)

    @jwt_required()
    @permission_filter(0xff)
    def post(self):
        data = request.get_json()
        name = data.get('name')

        new_project = Project(name=name)

        new_project.save()
        return util.api_response(data={'msg': 'success'})

    @jwt_required()
    @permission_filter(0xff)
    def delete(self, id=None):
        if not id:
            raise ValueError('Not find id!')

        project = Project.get_by_id(id=id)

        project.delete()
        return util.api_response(data={'msg': 'success'})
