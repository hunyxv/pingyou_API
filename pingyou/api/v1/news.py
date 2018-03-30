from flask import request
from flask_jwt import jwt_required

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.service.user import permission_filter, get_current_user
from pingyou.models import News
from pingyou.common import util


@api.route('/api/v1/news', endpoint='news')
class NewsAPI(BaseAPI):
    @jwt_required()
    def get(self):
        me = get_current_user()
        if me.role.permissions >= 0x33:
            news = News.objects(department=me.department).first()
        else:
            news = News.objects(department=me.department.up_one_level).first()
        return util.api_response(data=news.api_response())

    @jwt_required()
    @permission_filter(0x33)
    def post(self, ):
        me = get_current_user()
        data = request.get_json()
        post = data.get('news')
        news = News.objects(department=me.department, _class=me._class).first()
        if not news:
            news = News(
                department=me.department,
                _class=me._class,
                author=me,
                news=util.clear_str(post)
            )

            news.save()
        else:
            news.news = util.clear_str(post)
            news.save()

        return util.api_response(data={'msg': 'success'})
