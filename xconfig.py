import os


class Config(object):
    def __init__(self):
        self.APP_NAME = 'Best Community Service'

        self.ENV = 'dev'
        self.SECRET_KEY = os.environ.get('SECRET_KEY') or '\x84\x97\x10\x3d\x1a\x7b\x92\xea\xb8\xc7\xd4\x29\xf1\x1d\xdb\x88\x05\x8b\x1c\x24\x48\x69\xbc\xf3\x82\x74\xac\x1a\x4a\x63\x76\x44\x09\x24\x6b\xab\xb2\xdb\x68\xa1\xae\x30\x53\x92\x04\x82\xde\x5e\x96\x1a\x4f\x4f\x44\x2b\x66\xe9\x92\x00\x2f\xe8\xdd\x81\x0e\x23\x7d\xac\xf2\x3d\xdb\xe6'

        self.MAX_CONTENT_LENGTH = 20000000
        self.DEBUG = True

        self.PROJECT_DIR = os.path.dirname(__file__)

        connection_string = "mysql+pymysql://root:password@127.0.0.1:3306/bcs"
        self.SQLALCHEMY_DATABASE_URI = connection_string
        self.SQLALCHEMY_POOL_SIZE = 20
        self.SQLALCHEMY_POOL_RECYCLE = 60 * 60
        # this app does not utilize about SQLAlchemy events
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """ default/dev config. dev is default to prevent production corruption """
    def __init__(self):
        super(DevelopmentConfig, self).__init__()
        self.DEBUG = True
        self.ENV = 'dev'


config = {
    'default': DevelopmentConfig,
    'dev': DevelopmentConfig,
}


def get_config(env):
    return config['default']()
