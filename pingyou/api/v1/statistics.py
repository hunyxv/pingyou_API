import datetime

import os
from flask import request, send_from_directory, make_response
from flask_jwt import jwt_required
from flask_restful import reqparse, inputs

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import ProjectDetail, Department, Ballot
from pingyou.common import util, redis_handle, exceltable

parser = reqparse.RequestParser()


@api.route('/api/v1/stat', endpoint='stat')
class StatAPI(BaseAPI):
    # @jwt_required()
    def get(self):
        year = datetime.datetime.today().year
        period = [year-4, year-3, year-2, year-1]
        if datetime.datetime.today().month in [9,10,11,12]:
            period.append(year)

        parser.add_argument('item', type=str, default=None)
        parser.add_argument('project', type=str, default=None)
        parser.add_argument('period', type=int, default=None)
        parser.add_argument('department', type=str, default=None)
        parser.add_argument('download', type=inputs.boolean, default=False)
        parser.add_argument('status', type=int, default=3)

        args = parser.parse_args()
        item = args['item']
        download = args['download']

        query = self.deal_query_param(args,item)
        project_detailList = ProjectDetail.objects(**query).order_by('-create_date')

        if not download:
            data = [item.api_response() for item in project_detailList]
            return util.api_response(data=data)

        department_list = Department.objects(up_one_level=None)
        data = {}
        for department in department_list:
            data[department.name] = [item for item in project_detailList if item.department in Department.objects(up_one_level=department)]
        #print(data)
        data_list = [['项目名','项目类别','班级','辅导员','名额','申请者','评选结果']]
        for k,v in data.items():
            data_list.append([k])
            for l in v:
                participants = ''
                for p in l.participants:
                    participants += str(p)+','
                result = ''
                for r in l.result:
                    result += str(r)+','
                data_list.append([
                    l.name,
                    l.project.name,
                    l._class.name,
                    l.counselor.name,
                    l.places,
                    participants,
                    result
                ])

        fileName = exceltable.writeExcel(data_list)

        print(os.getcwd() + '/files/' + fileName)
        response = make_response(send_from_directory(os.getcwd() + '/files/', fileName, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(os.getcwd() + '/files/' + fileName.encode().decode('latin-1'))
        return response


    def deal_query_param(self, args, item):
        query = {}

        if args['project'] is not None:
            query['project'] = args['project']
        if args['period'] is not None:
            query['period'] = args['period']
        if args['status'] is not None:
            query['status'] = args['status']
        if args['department'] is not None:
            if item == 'all':
                pass
            else:
                query['department'] = args['department']

        return query
