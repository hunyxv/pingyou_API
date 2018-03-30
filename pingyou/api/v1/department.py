from flask import request
from flask_jwt import jwt_required

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import permission_filter, get_current_user
from pingyou.models import Department
from pingyou.common import util


@api.route('/api/v1/department', endpoint='department')
@api.route('/api/v1/department/<string:id>', endpoint='department_del')
class DepartmentAPI(BaseAPI):
    @jwt_required()
    def get(self):
        me = get_current_user()
        if me.role.permissions == 0x33:
            departent_list = Department.objects(up_one_level=me.department)
            data = [item.api_response() for item in departent_list]
        else:
            data = [me.department.api_response()]
        return util.api_response(data=data)

    @jwt_required()
    @permission_filter(0xff)
    def post(self):
        data = request.get_json()
        up_one_level = data.get('up_one_level')
        name = data.get('name')

        new_department = Department(up_one_level=up_one_level, name=name)

        new_department.save()
        return util.api_response(data={'msg': 'success'})

    @jwt_required()
    @permission_filter(0xff)
    def delete(self, id=None):
        if not id:
            raise ValueError('Not find id!')

        department = Department.get_by_id(id=id)

        department.delete()
        return util.api_response(data={'msg': 'success'})