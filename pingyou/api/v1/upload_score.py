import openpyxl
import datetime

from flask import request
from flask_jwt import jwt_required
from flask_restful import reqparse

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import get_current_user, permission_filter
from pingyou.models import User, Score
from pingyou.common import util, redis_handle


@api.route('/api/v1/upload', endpoint="upload")
class UpdateAPI(BaseAPI):
    @jwt_required()
    def get(self):
        me = get_current_user()
        month = [8, 9, 10, 11, 12]
        # 当前学期
        term = ((datetime.date.today().year - me.enrollment_date.year) * 2 +
                [1 if datetime.date.today().month in month else 0][0])
        users = [
            user for user in
            User.objects(department=me.department, _class = me._class)
            if user.period == me.period
        ]
        scoreList = Score.objects(student__in=users, term = term-1)
        data = [item.api_response() for item in scoreList]

        return util.api_response(data=data)

    @jwt_required()
    @permission_filter(0x0f)
    def post(self):
        files = request.files.get('excelFile.xlsx', None)
        print(files)
        if not files:
            return util.api_response(data={'msg': '上传出错'})
        allow_suffix = ['et', 'xls', 'xlsx']
        files_suffix = files.name.split('.')[-1]
        if files_suffix not in allow_suffix:
            return util.api_response(data={'msg': '文件格式出错'})

        excel = openpyxl.load_workbook(files)
        sheet = excel.get_sheet_by_name(excel.get_sheet_names()[0])
        values = []
        for v in sheet.values:
            values.append(v)
        # (id , name, term, score, guake, jiguo)
        for row in values[1:]:
            student = User.objects(s_id=row[0]).first()
            if student:
                score = Score.objects(student=student, term=row[2]).first()
                if score:
                    score.score = row[3]
                    score.guake=[False if row[4] == 'N' or row[4] == 'n' else True][0]
                    score.jiguo=[False if row[5] == 'N' or row[5] == 'n' else True][0]
                else:
                    score = Score(student=student,
                                  term=row[2], score=row[3],
                                  guake=[False if row[4] == 'N' or row[4] == 'n' else True][0],
                                  jiguo=[False if row[5] == 'N' or row[5] == 'n' else True][0]
                                  )
                score.save()

        return util.api_response(data={'msg': 'success'})