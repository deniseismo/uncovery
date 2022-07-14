import pickle
import random
from dataclasses import asdict

import tekore as tk
from flask import current_app, session

from uncover import cache
from uncover.models import User
from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client
from uncover.profile.spotify.prepare_tracks import extract_albums_from_spotify_tracks


def get_spotify_auth():
    """
    get a User auth object
    :return: redirect url
    """
    conf = (
        current_app.config['SPOTIFY_CLIENT_ID'],
        current_app.config['SPOTIFY_CLIENT_SECRET'],
        current_app.config['SPOTIFY_REDIRECT_URI']
    )
    cred = tk.Credentials(*conf)
    # scopes allow client to read user's name, id, avatar & user's top artists/tracks
    scope = tk.Scope(tk.scope.user_top_read, tk.scope.user_read_private)
    auth = tk.UserAuth(cred, scope)
    return auth


def check_spotify():
    """
    checks if the person's logged in and the token's not expired
    refreshes token if present
    :return: (user, token)
    """
    user = session.get('user', None)
    token = session.get('token', None)
    if token:
        token = pickle.loads(session.get('token', None))

    if user is None or token is None:
        print('something is None')
        session.pop('user', None)
        session.pop('token', None)
        return None, None

    if token.is_expiring:
        # get new access token
        print('token is expiring')
        conf = (
            current_app.config['SPOTIFY_CLIENT_ID'],
            current_app.config['SPOTIFY_CLIENT_SECRET'],
            current_app.config['SPOTIFY_REDIRECT_URI']
        )
        print(user)
        cred = tk.Credentials(*conf)
        user_entry = User.query.filter_by(spotify_id=user).first()
        if user_entry:
            print(f'user found: {user}')
            # get user's refresh token from db
            refresh_token = user_entry.spotify_token
            if refresh_token:
                # get new token via refresh token
                token = cred.refresh_user_token(refresh_token)
                session['token'] = pickle.dumps(token)

    return user, token


@cache.memoize(timeout=60000)
def get_spotify_user_info(token):
    """
    get information about the current spotify user
    :param token: a Spotify access token
    :return: user info {username, user_image}
    """
    print('getting user info...')
    print(token)
    spotify_tekore_client = get_spotify_tekore_client()
    try:
        with spotify_tekore_client.token_as(token):
            print('getting here')
            current_user = spotify_tekore_client.current_user()
            username = current_user.display_name
            current_user_image_list = current_user.images
            country = current_user.country
            if current_user_image_list:
                try:
                    user_image = current_user.images[0].url
                except (KeyError, IndexError, TypeError):
                    user_image = None
            else:
                user_image = None

    except tk.HTTPError:
        return None
    user_info = {
        "username": username,
        "user_image": user_image,
        "country": country
    }
    return user_info


@cache.memoize(timeout=3600)
def spotify_get_users_albums(token):
    """
    get current spotify user top albums
    :param token: an access token
    :return: a dict {album_title: album_image_url}
    """
    time_periods = ['short_term', 'medium_term', 'long_term']
    if not token:
        return None
    spotify_tekore_client = get_spotify_tekore_client()
    try:
        with spotify_tekore_client.token_as(token):
            # get user's top 50 tracks
            top_tracks = spotify_tekore_client.current_user_top_tracks(limit=50, time_range=random.choice(time_periods))
    except tk.HTTPError:
        return None

    if not top_tracks:
        return None

    # initialize a dict to avoid KeyErrors
    album_info = {
        "info": {
            "type": "playlist",
            "query": f"top tracks by some user"  # TODO: get user's name or something
        },
        "albums": []
    }
    albums = extract_albums_from_spotify_tracks(top_tracks.items)
    if not albums:
        return None
    album_info["albums"] = [asdict(album) for album in albums]
    return album_info
