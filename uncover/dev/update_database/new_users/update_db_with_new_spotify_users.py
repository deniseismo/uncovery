from uncover import db
from uncover.models import User


def add_spotify_user_to_database(user_id, spotify_token):
    if not user_id or not spotify_token:
        print("not enough data provided")
        return False
    if not isinstance(user_id, str) or not isinstance(spotify_token, str):
        print("incorrect data type")
        return False
    a_user = User(spotify_id=user_id, spotify_token=spotify_token)
    db.session.add(a_user)
    db.session.commit()