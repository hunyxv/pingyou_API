import datetime

from flask import request
from flask_jwt import jwt_required
from flask_restful import reqparse, inputs

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import ProjectDetail, _Class, Permission, Department
from pingyou.common import util, redis_handle

parser = reqparse.RequestParser()


@api.route('/api/v1/project-detail', endpoint="project_detail")
@api.route('/api/v1/project-detail/<string:id>', endpoint="project_all")
class ProjectDetailAPI(BaseAPI):
    @jwt_required()
    def get(self, id=None):
        if not id:
            parser.add_argument('status', type=int, default=1)
            args = parser.parse_args()
            status = args.get('status')

            me = get_current_user()
            if me.role.permissions >= 0x33:
                department_list = Department.objects(up_one_level=me.department)
                project_detailList = ProjectDetail.objects(department__in=department_list, status=status)
            else:
                project_detailList = ProjectDetail.objects(department=me.department, _class=me._class, status=status)
            data = [item.api_response() for item in project_detailList]
            return util.api_response(data=data)

        project_detail = ProjectDetail.get_by_id(id=id)
        return util.api_response(data=project_detail.api_response())

    @jwt_required()
    @permission_filter(0x33)
    def post(self):
        me = get_current_user()
        data = request.get_json()

        name = data['name']
        project_id = data['project_id']
        department_list = data['department_list']
        _class_list = data['class_list']
        places = data['places']
        exp = data['exp']
        response_data = []
        my_departments = [item.id for item in Department.objects(up_one_level=me.department)]

        for department in department_list:
            if department in my_departments:
                for _class in _class_list:
                    if not ProjectDetail.objects(name=name, department=department, _class=_Class.query(_class)):
                        new_project_detail = ProjectDetail(
                            name=name,
                            project=project_id,
                            department=department,
                            _class=_Class.query(_class),
                            counselor=me,
                            places=places,
                            exp=[exp if exp else 7][0]
                        )
                        new_project_detail.save()
                        response_data.append(new_project_detail.api_response())
        return util.api_response(data=response_data)

    @jwt_required()
    @permission_filter(0x33)
    def put(self, id=None):
        if not id:
            raise ValueError('Id is not find!')

        project_detail = ProjectDetail.get_by_id(id=id)

        data = request.get_json()
        project_detail.update(data)
        return util.api_response(data=project_detail.api_response())

    @jwt_required()
    @permission_filter(0x33)
    def delete(self, id=None):
        if not id:
            raise ValueError('Id is not find!')

        project_detail = ProjectDetail.get_by_id(id=id)

        project_detail.status = 2
        project_detail.save()
        return util.api_response(data={'msg': 'success'})