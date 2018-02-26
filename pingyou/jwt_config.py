import datetime
from flask_jwt import JWT

from pingyou import app, api
from pingyou.models.user import authenticate, identity
from pingyou.common import util

jwt = JWT(app, authenticate, identity)

# 构造载荷
@jwt.jwt_payload_handler
def jwt_payload_handler(identity):
    iat = datetime.datetime.utcnow()
    exp = iat + app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + app.config.get('JWT_NOT_BEFORE_DELTA')
    identity = getattr(identity, 'id', None) or identity['id']
    return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': str(identity)}

@jwt.auth_response_handler
def auth_response_handler(access_token, identity):
    # data = {'access_token': access_token.decode('utf-8')}
    # return util.api_response(data=data)
    data = {'access_token': access_token.decode('utf-8')}
    return api.make_response(*util.api_response(data=data))
