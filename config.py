# coding=utf-8
import os
import datetime

basesdir = os.path.abspath(os.path.dirname(__name__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'c\x05\xe7\xfd,\x98\xf5\xba\x17\xffg\xc0\\\xe2e\x1eX\x0e\xd7D.\xa1t\x8e'
    FLASKY_MAIL_SENDER = '15127860671@163.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or '1035794358@qq.com'
    FLASKY_MAIL_SUBJECT_PREFIX = '[评优评先系统]'
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 20
    FLASKY_COMMENTS_PER_PAGE = 20
    JWT_AUTH_URL_RULE = None
    JWT_EXPIRATION_DELTA = datetime.timedelta(days=14)

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_POST = 465  # 或994
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '15127860671@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'xxxxxx'
    MONGODB_SETTINGS = {
        'db': 'pingyou',
        'host': '127.0.0.1',
        'port': 27017
    }


class TestingConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = {
        'db': 'pingyou',
        'host': '127.0.0.1',
        'port': 27017
    }


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'db': 'pingyou',
        'host': '127.0.0.1',
        'port': 27017
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
