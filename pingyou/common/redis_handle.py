import redis

from pingyou.common import util

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)

r = redis.Redis(connection_pool=pool)


def save_hash(key, field=None, value=None):
    """
    对于某个priject_detail, 每个人投票次数的限制， 和此次投票过期时间的设置
    :param key: project_detail.id
    :param field: user.s_id or user.id
    :param value: 剩余投票数
    :param project_detail: project_detail
    :return:
    """
    if not value:
        times = int(get_value(key, 'hash', field=field).decode('utf8'))
        if not times:
            return False
        r.hset(str(key), str(field), times-1)
        return True
    else:
        r.hset(str(key), str(field), value)


def initialize(key, exp):
    r.hset(str(key),'1','1')
    r.expire(str(key), exp * 24 * 60 * 60)


def save_code(key, code):
    """
    在redis中存储验证码
    :param key: user.id
    :param code: str
    :return:
    """
    r.setex(str(key), code, 300)


def get_value(key, _type, field=None):
    """
    从redis中获取键的内容，或hash某属性的值
    :param key: user.id or project_detail.id ,eq...
    :param _type: string hash set eq...
    :param field: hash 的字段属性
    :return:
    """
    if _type == 'string':
        return r.get(str(key)).decode('utf8')
    if _type == 'hash':
        # if not field:
        #     return r.hvals(str(key)).decode('utf8')
        return r.hget(str(key), str(field))


def exp_time(key):
    """
    获取某个键的剩余时间
    :param key:
    :return:
    """
    return r.ttl(str(key))