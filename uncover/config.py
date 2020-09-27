import os


class Config:
    SERVER_NAME = '192.168.1.62:5000'
    JSON_SORT_KEYS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
