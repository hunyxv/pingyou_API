import re
import string
import random

from pingyou.common import redis_handle


def clear_str(s):
    dr = re.compile(r'</?\w+[^>]*>', re.S)
    s = re.sub(dr, '', s)
    return s


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
