import pickle
import random
from typing import Optional

import tekore as tk
from flask import current_app, session

from uncover import cache
from uncover.album_processing.album_processing_helpers import sort_artist_albums, enumerate_artist_albums
from uncover.album_processing.process_albums_from_spotify import extract_albums_from_spotify_tracks
from uncover.models import User
from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client
from uncover.schemas.album_schema import AlbumInfo
from uncover.schemas.spotify_user_info import SpotifyUserAuth, SpotifyUserProfile


def get_spotify_auth() -> tk.UserAuth:
    """
    get a tekore spotify User auth object
    :return: (tk.UserAuth)
    """
    conf = _get_app_spotify_credentials()
    cred = tk.Credentials(*conf)
    # scopes allow client to read user's name, id, avatar & user's top artists/tracks
    scope = tk.Scope(tk.scope.user_top_read, tk.scope.user_read_private)
    auth = tk.UserAuth(cred, scope)
    return auth


def authenticate_spotify_user() -> Optional[SpotifyUserAuth]:
    """
    checks/authenticates spotify user; refreshes token if present
    :return: (SpotifyUserAuth) with spotify user id and access token
    """
    user = session.get('user', None)
    token = session.get('token', None)
    if token:
        token = pickle.loads(session.get('token', None))

    if not (user and token):
        session.pop('user', None)
        session.pop('token', None)
        return SpotifyUserAuth(None, None)

    if token.is_expiring:
        # get new access token
        conf = _get_app_spotify_credentials()
        cred = tk.Credentials(*conf)
        user_entry = User.query.filter_by(spotify_id=user).first()
        if user_entry:
            # get user's refresh token from db
            refresh_token = user_entry.spotify_token
            if refresh_token:
                # get new token via refresh token
                token = cred.refresh_user_token(refresh_token)
                session['token'] = pickle.dumps(token)

    return SpotifyUserAuth(user, token)


@cache.memoize(timeout=60000)
def get_spotify_user_info(token) -> Optional[SpotifyUserProfile]:
    """
    get information about the current spotify user
    :param token: a Spotify access token
    :return: (SpotifyUserProfile) with spotify user info (username, avatar, country)
    """
    spotify_tekore_client = get_spotify_tekore_client()
    if not spotify_tekore_client:
        return None
    try:
        with spotify_tekore_client.token_as(token):
            current_user = spotify_tekore_client.current_user()

            username = current_user.display_name
            country = current_user.country
            user_image = None
            current_user_image_list = current_user.images
            if current_user_image_list:
                try:
                    user_image = current_user.images[0].url
                except (IndexError, TypeError) as e:
                    print(e)
    except tk.HTTPError:
        return None
    return SpotifyUserProfile(username=username, user_image=user_image, country=country)


def spotify_get_users_albums(token) -> Optional[list[AlbumInfo]]:
    """
    get current spotify user top albums
    :param token: an access token
    :return: ([list[AlbumInfo]) of spotify user top albums (in reality, albums from top tracks)
    """
    time_ranges = ['short_term', 'medium_term', 'long_term']
    time_range = random.choice(time_ranges)
    albums = _spotify_get_users_albums_for_specific_time_range(token, time_range)
    sort_artist_albums(albums, sorting="shuffle")
    albums = albums[:9]
    enumerate_artist_albums(albums)
    return albums


@cache.memoize(timeout=3600)
def _spotify_get_users_albums_for_specific_time_range(token, time_range: str) -> Optional[list[AlbumInfo]]:
    """
    separate function for getting spotify user's albums for different time range;
    makes it easy to 'memoize' search results for the pair (token (specific user) and time range picked beforehand)
    :param token: spotify user access token
    :param time_range: (str) one of the ['short_term', 'medium_term', 'long_term'] spotify-specific time range types
    :return: (list[AlbumInfo]) AlbumIfo albums extracted from spotify user's top track for a time range specified
    """
    spotify_tekore_client = get_spotify_tekore_client()
    if not spotify_tekore_client:
        return None
    try:
        with spotify_tekore_client.token_as(token):
            # get user's top 50 tracks
            top_tracks = spotify_tekore_client.current_user_top_tracks(
                limit=50,
                time_range=time_range
            )
    except tk.HTTPError:
        return None

    if not top_tracks:
        return None
    albums = extract_albums_from_spotify_tracks(top_tracks.items)
    if not albums:
        return None
    return albums


def _get_app_spotify_credentials() -> tuple[str, str, str]:
    """
    get spotify client credentials [client id, client secret, redirect uri]
    :return: (tuple[str, str, str]) spotify credentials [client id, client secret, redirect uri]
    """
    return (
        current_app.config['SPOTIFY_CLIENT_ID'],
        current_app.config['SPOTIFY_CLIENT_SECRET'],
        current_app.config['SPOTIFY_REDIRECT_URI']
    )
