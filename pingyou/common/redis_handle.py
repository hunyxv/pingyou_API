import redis

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)

r = redis.Redis(connection_pool=pool)


def save_code(key, code):
    r.setex(str(key), code, 300)


def get_code(key):
    return r.get(str(key)).decode('utf8')


def exp_time(key):
    return r.ttl(str(key))