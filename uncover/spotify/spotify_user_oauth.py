import pickle

import tekore as tk
from flask import current_app, Blueprint, session
from fuzzywuzzy import fuzz

import uncover.helpers.utilities as utils
from uncover import cache
from uncover.models import User

spotify = Blueprint('spotify', __name__)

spotify_tekore_client = tk.Spotify()


def get_spotify_auth():
    """
    get a User auth object
    :return: redirect url
    """
    conf = (
        current_app.config['SPOTIPY_CLIENT_ID'],
        current_app.config['SPOTIPY_CLIENT_SECRET'],
        current_app.config['SPOTIPY_REDIRECT_URI']
    )
    cred = tk.Credentials(*conf)
    # scopes allow client to read user's name, id, avatar & user's top artists/tracks
    scope = tk.Scope(tk.scope.user_top_read, tk.scope.user_read_private)
    auth = tk.UserAuth(cred, scope)
    return auth


def check_spotify():
    """
    checks if the person's logged in the token's not expired
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
            current_app.config['SPOTIPY_CLIENT_ID'],
            current_app.config['SPOTIPY_CLIENT_SECRET'],
            current_app.config['SPOTIPY_REDIRECT_URI']
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

    :param token: a Spotify access token
    :return: user info {username, user_image}
    """
    print('getting user info...')
    print(token)
    try:
        with spotify_tekore_client.token_as(token):
            print('getting here')
            current_user = spotify_tekore_client.current_user()
            username = current_user.display_name
            current_user_image_list = current_user.images
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
        "user_image": user_image
    }
    return user_info


@cache.memoize(timeout=3600)
def spotify_get_users_albums(token):
    """
    :param token: an access token
    :return: a dict {album_title: album_image_url}
    """
    print('spotify getting albums')
    if not token:
        return None
    try:
        with spotify_tekore_client.token_as(token):
            # get user's top 50 tracks
            top_tracks = spotify_tekore_client.current_user_top_tracks(limit=50)
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
    # initialize a set of titles used to filter duplicate titles
    list_of_titles = set()
    # iterate through tracks
    for track in top_tracks.items:
        if track.album.album_type == 'album':
            name = track.album.name
            filtered_title = utils.get_filtered_name(name)
            filtered_title = utils.remove_punctuation(filtered_title)
            artist_name = track.artists[0].name
            an_album_dict = {
                "artist_name": artist_name,
                "artist_names": [artist_name] + utils.get_filtered_names_list(artist_name),
                "title": name,
                "names": [name.lower()] + utils.get_filtered_names_list(name),
                "image": track.album.images[0].url,
                "rating": track.popularity,
                "spotify_id": track.album.id,
                "year": track.album.release_date[:4]
            }
            an_album_dict["artist_names"] = list(set(an_album_dict["artist_names"]))
            an_album_dict['names'] = list(set(an_album_dict['names']))
            # filter duplicates:
            if filtered_title not in list_of_titles:
                # append a title to a set of titles
                list_of_titles.add(filtered_title)
                # adds an album info only if a title hasn't been seen before
                album_info["albums"].append(an_album_dict)
    if not album_info['albums']:
        return None
    return album_info


def spotify_get_album_id(album_name, artist_name):
    """
    gets Spotify album id with through Tekore
    :param album_name: album's title
    :param artist_name: artist's title
    :return: Spotify album id
    """
    # TODO: cache the function taking into account country restrictions
    transliterated = False
    artist_name = artist_name.lower().replace('the ', '')
    query = "album:" + album_name + " artist:" + artist_name
    user, token = check_spotify()
    if user and token:
        try:
            with spotify_tekore_client.token_as(token):
                album_info = spotify_tekore_client.search(
                    query=query,
                    types=('album',),
                    market='from_token',
                    limit=5
                )
                if album_info:
                    if not album_info[0].items:
                        if utils.has_cyrillic(artist_name):
                            artist_name = utils.transliterate(artist_name)
                            query = "album:" + album_name + " artist:" + artist_name
                            album_info = spotify_tekore_client.search(
                                query=query,
                                types=('album',),
                                market='from_token',
                                limit=5
                            )
                            print(artist_name)
        except tk.HTTPError:
            return None
        if not album_info:
            return None
        print(len(album_info[0].items))
        album_items = album_info[0].items
        if not album_items:
            return None
        artist_name = artist_name.lower().replace(' & ', ' and ')
        album_name = utils.get_filtered_name(album_name)
        ratio_threshold = 94
        album_id_found = None
        for album in album_items:
            print(album.name)
            try:
                current_artist = album.artists[0].name. \
                    lower().replace(' & ', ' and ').replace('the ', '')
                current_album = utils.get_filtered_name(album.name)

                current_artist_ratio = fuzz.ratio(artist_name, current_artist)
                current_album_ratio = fuzz.ratio(album_name, current_album)
                if current_album_ratio > 98 and current_artist_ratio > 90:
                    # found perfect match, return immediately
                    return album.id
                elif current_album_ratio > ratio_threshold and current_artist_ratio > 90:
                    ratio_threshold = current_album_ratio
                    album_id_found = album.id
            except (KeyError, TypeError, IndexError):
                continue
        return album_id_found
    return None
