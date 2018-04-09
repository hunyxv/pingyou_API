from flask_restful import reqparse

from pingyou import api
from pingyou.api.base import BaseAPI
from pingyou.models import WeChat
from pingyou.common import util

parser = reqparse.RequestParser()

@api.route('/api/v1/wechat', endpoint='wechat')
class WeChatAPI(BaseAPI):
    def get(self):
        parser.add_argument('page', type=int, default=1)
        parser.add_argument('page_size', type=int, default=8)
        args = parser.parse_args()

        page = args.get('page')
        page_size = args.get('page_size')

        wechatList = util.paging(
                    cls=WeChat,
                    page=page,
                    page_size=page_size,
                    query={},
                    order_by=['-date']
                )
        wechatList['list'] = [
            item.api_response() for item in wechatList['list']
        ]
        return util.api_response(data=wechatList)
