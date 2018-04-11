from flask import request
from flask_jwt import jwt_required

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import permission_filter
from pingyou.models import _Class
from pingyou.common import util


@api.route('/api/v1/class', endpoint='class')
@api.route('/api/v1/class/<string:id>', endpoint='class_del')
class ClassAPI(BaseAPI):
    def get(self):
        class_list = _Class.objects()
        data = [item.api_response() for item in class_list]

        return util.api_response(data=data)

    @jwt_required()
    @permission_filter(0xff)
    def post(self):
        data = request.get_json()
        name = data.get('class')
        if _Class.objects(name=name):
            new_class = _Class(name=name)

            new_class.save()
            return util.api_response(data={'msg': 'success'})
        return util.api_response(data={'msg': 'already have'})

    @jwt_required()
    @permission_filter(0xff)
    def delete(self, id=None):
        if not id:
            raise ValueError('Not find id!')

        _class = _Class.get_by_id(id=id)

        _class.delete()
        return util.api_response(data={'msg': 'success'})