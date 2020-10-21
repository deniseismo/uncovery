import json

with open("etc/config.json") as config_file:
    config = json.load(config_file)


class Config:
    SERVER_NAME = '192.168.1.62:5000'
    JSON_SORT_KEYS = False
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    API_KEY = config.get('API_KEY')
    SECRET_KEY = config.get('SECRET_KEY')
    SPOTIPY_CLIENT_SECRET = config.get("SPOTIPY_CLIENT_SECRET")
    SPOTIPY_CLIENT_ID = config.get("SPOTIPY_CLIENT_ID")
    MUSIC_BRAINZ_USER_AGENT = config.get("MUSIC_BRAINZ_USER_AGENT")
    DISCOGS_USER_TOKEN = config.get("DISCOGS_USER_TOKEN")
    USER_AGENT = config.get("USER_AGENT")
