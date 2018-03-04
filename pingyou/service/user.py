import functools
from flask import _request_ctx_stack

from pingyou.models import Role


def get_current_user():
    return _request_ctx_stack.top.current_identity


def permission_filter(permission=None):
    if not permission:
        permission = 0xff

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user.can(permission):
                raise Exception("User don't have permissionro access!")
            return func(*args, **kwargs)

        return wrapper
    return decorator
