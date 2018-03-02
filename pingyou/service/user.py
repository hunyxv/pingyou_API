from flask import _request_ctx_stack


def get_current_user():
    return _request_ctx_stack.top.current_identity