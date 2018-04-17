import datetime

from flask import request
from flask_jwt import jwt_required
from flask_restful import reqparse

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import ProjectDetail, Department, Ballot
from pingyou.common import util, exceltable

parser = reqparse.RequestParser()


@api.route('/api/v1/project-detail', endpoint="project_detail")
@api.route('/api/v1/project-detail/<string:id>', endpoint="project_all")
class ProjectDetailAPI(BaseAPI):
    @jwt_required()
    def get(self, id=None):
        if not id:
            parser.add_argument('page', type=int, default=1)
            parser.add_argument('page_size', type=int, default=8)
            parser.add_argument('status', type=int, default=None)

            args = parser.parse_args()

            page = args.get('page')
            page_size = args.get('page_size')
            status = args.get('status')

            me = get_current_user()
            if me.role.permissions >= 0x33:
                department_list = Department.objects(up_one_level=me.department)
                query = {'department__in': department_list, 'status__ne': 4}
                if status:
                    query = {'department__in': department_list, 'status': status}
                project_detailList = util.paging(
                    cls=ProjectDetail,
                    page=page,
                    page_size=page_size,
                    query=query,
                    order_by=['-create_date']
                )
            else:
                if status is not None:
                    if ProjectDetail.objects(department= me.department, _class= me._class, status= 1):
                        status = 1
                    query = {'department': me.department, '_class': me._class, 'status': status}
                else:
                    query = {'department': me.department, '_class': me._class, 'status__ne': 4}
                project_detailList = util.paging(
                    cls=ProjectDetail,
                    page=page,
                    page_size=page_size,
                    query=query,
                    order_by=['-create_date']
                )
            project_detailList['list'] = [
                item.api_response()
                for item in project_detailList['list']
            ]
            return util.api_response(data=project_detailList)

        project_detail = ProjectDetail.get_by_id(id=id)
        return util.api_response(data=project_detail.api_response())

    @jwt_required()
    @permission_filter(0x33)
    def post(self):
        me = get_current_user()
        data = request.get_json()

        year = datetime.datetime.today().year
        period = [year - 4, year - 3, year - 2, year - 1]
        if datetime.datetime.today().month in [9, 10, 11, 12]:
            period.append(year)

        name = data['name']
        project_id = data['project']
        department_list = data['department_list']
        _class_list = data['class_list']
        places = data['places']
        periods = data.get('period_list', period)
        exp = data['exp']
        my_departments = [str(item.id) for item in Department.objects(up_one_level=me.department)]

        for period in periods:
            for department in department_list:
                if department in my_departments:
                    for _class in _class_list:

                        new_project_detail = ProjectDetail(
                            name=name,
                            project=project_id,
                            department=department,
                            _class=_class,
                            counselor=me,
                            places=places,
                            period=period,
                            exp=[exp if exp else 7][0]
                        )
                        new_project_detail.save()

        return util.api_response(data={'msg': 'success'})

    @jwt_required()
    def put(self, id=None):
        if not id:
            raise ValueError('Id is not find!')
        me = get_current_user()
        project_detail = ProjectDetail.get_by_id(id=id)

        data = request.get_json()
        if 'status' in data and data['status'] == 3:
            ballot_list = Ballot.objects(project_detail=project_detail).order_by('-number')
            data['result'] = [item.people.s_id for item in ballot_list[:project_detail.places]]
            project_detail.update(data)

            data = [['姓名', '项目名', '得票数', '总积分']]
            for ballot in ballot_list[:project_detail.places]:
                row = [ballot.people.name, project_detail.name, ballot.number, ballot.integration]
                data.append(row)
            filename = exceltable.writeExcel(data=data)

            return util.api_response(data={'msg': filename})

        if me.role.name == 'Monitor' and (len(data) != 1 or 'status' not in data) :
            return util.api_response({'msg': 'you can not change!'})

        project_detail.update(data)
        return util.api_response(data={'msg': 'success'})

    @jwt_required()
    @permission_filter(0x33)
    def delete(self, id=None):
        if not id:
            raise ValueError('Id is not find!')

        project_detail = ProjectDetail.get_by_id(id=id)

        project_detail.status = 4
        project_detail.save()
        return util.api_response(data={'msg': 'success'})