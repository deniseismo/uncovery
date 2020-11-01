import json
from datetime import timedelta

with open("etc/config.json") as config_file:
    config = json.load(config_file)


class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SEND_FILE_MAX_AGE_DEFAULT = 0
    SERVER_NAME = '192.168.1.62:5000'
    JSON_SORT_KEYS = False
    SESSION_COOKIE_NAME = 'uncovery-cookie'
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    API_KEY = config.get('API_KEY')
    SPOTIPY_CLIENT_SECRET = config.get("SPOTIPY_CLIENT_SECRET")
    SPOTIPY_CLIENT_ID = config.get("SPOTIPY_CLIENT_ID")
    MUSIC_BRAINZ_USER_AGENT = config.get("MUSIC_BRAINZ_USER_AGENT")
    DISCOGS_USER_TOKEN = config.get("DISCOGS_USER_TOKEN")
    USER_AGENT = config.get("USER_AGENT")
    SPOTIPY_REDIRECT_URI = config.get("SPOTIPY_REDIRECT_URI")
    PERMANENT_SESSION_LIFETIME = timedelta(days=5)
