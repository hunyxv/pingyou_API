import re
import string
import random

from pingyou.common import redis_handle
from mongoengine import Document


def clear_str(s):
    dr = re.compile(r'</?\w+[^>]*>', re.S)
    s = re.sub(dr, '', s)
    return s.strip()


def paging(cls=None, field=None, page=None, page_size=None, order_by=None,
           query=None):
    if query is None:
        query = {}
    if page is None:
        page = 1
    if page_size is None:
        page_size = 10
    if order_by is None:
        order_by = []
    if not isinstance(cls(), Document):
        raise 'Class is not extend mongoengine.Document'

    def get_limit(count, page, page_size):
        if page <= 0:
            page = 1
        page_sum = int((count - 1) / page_size + 1)
        start = (page - 1) * page_size
        has_previous = True if page > 1 else False
        has_next = True if page < page_sum else False
        return {'start': start, 'page_sum': page_sum,
                'has_next': has_next, 'has_previous': has_previous,
                'count': count}

    count = len(cls.objects(**query))
    results = get_limit(count, page, page_size)
    qery_set = cls.objects(**query).order_by(*order_by)
    list_ = qery_set.skip(results['start']).limit(page_size)
    # results['list'] = json.loads(list_.to_json())

    results['list'] = list_
    results['current_page'] = page
    results.pop('start', None)
    return results

def api_response(data=None, status_code=200):
    if data is None:
        data = {}
    return {'data': data}, status_code, {'Access-Control-Allow-Origin': '*'}


def generate_code(user):
    source = string.ascii_letters + string.digits
    code = ''.join(random.sample(source, 5))
    redis_handle.save_code(user.id, code)
    return code


def verify_code(user, code):
    try:
        r_code = redis_handle.get_value(str(user.id), _type='string')
    except AttributeError:
        raise Exception('Please resend the veriflcation code.')
    if r_code == code:
        return True
    return False
