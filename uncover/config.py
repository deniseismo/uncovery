import json
import os
from datetime import timedelta

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'etc'))
with open(os.path.join(file_path, 'config.json')) as config_file:
    config = json.load(config_file)


class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SEND_FILE_MAX_AGE_DEFAULT = 0
    #SERVER_NAME = '192.168.1.62:5000'
    JSON_SORT_KEYS = False
    SESSION_COOKIE_NAME = 'uncovery-cookie'
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    API_KEY = config.get('API_KEY')
    SPOTIFY_CLIENT_SECRET = config.get("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_CLIENT_ID = config.get("SPOTIFY_CLIENT_ID")
    MUSIC_BRAINZ_USER_AGENT = config.get("MUSIC_BRAINZ_USER_AGENT")
    DISCOGS_USER_TOKEN = config.get("DISCOGS_USER_TOKEN")
    USER_AGENT = config.get("USER_AGENT")
    SPOTIFY_REDIRECT_URI = config.get("SPOTIFY_REDIRECT_URI")
    APP_USER_AGENT = config.get("APP_USER_AGENT")
    PERMANENT_SESSION_LIFETIME = timedelta(days=5)
