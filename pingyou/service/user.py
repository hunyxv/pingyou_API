import functools
from flask import _request_ctx_stack

from pingyou.models import Role

Administrator = Role.objects(name='Administrator').first()
Counselor = Role.objects(name='Counselor').first()
Monitor = Role.objects(name='Monitor').first()


def get_current_user():
    return _request_ctx_stack.top.current_identity


def permission_filter(roles=None):
    if not roles:
        roles = [Administrator]

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user.role not in roles:
                raise Exception("User don't have permissionro access!")
            return func(*args, **kwargs)

        return wrapper
    return decorator
