import pickle

import tekore as tk
from flask import current_app
from flask import request, url_for, Blueprint, redirect, session, jsonify, make_response
from fuzzywuzzy import fuzz

import uncover.helpers.utilities as utils
from uncover import db, cache
from uncover.models import User

spotify = Blueprint('spotify', __name__)

spotify_tekore_client = tk.Spotify()

auths = {}  # Ongoing authorisations: state -> UserAuth


@spotify.route("/spotify_login", methods=['GET'])
def spotify_login():
    """
    get an authorization url and redirects to the spotify login page
    :return: redirect url
    """
    conf = (
        current_app.config['SPOTIPY_CLIENT_ID'],
        current_app.config['SPOTIPY_CLIENT_SECRET'],
        current_app.config['SPOTIPY_REDIRECT_URI']
    )
    cred = tk.Credentials(*conf)
    scope = tk.Scope(tk.scope.user_top_read, tk.scope.user_read_private)
    auth = tk.UserAuth(cred, scope)
    auths[auth.state] = auth
    return redirect(auth.url, 307)


@spotify.route('/spotify_logout', methods=['GET'])
def spotify_logout():
    user = session.pop('user', None)
    return redirect(url_for('main.home'), 307)


@spotify.route("/spotify_callback", methods=["GET"])
def spotify_callback():
    """
    a function that gets triggered after the user successfully granted the permission
    :return:
    """
    code = request.args.get('code', None)
    state = request.args.get('state', None)
    print(f'state {state}')
    auth = auths.pop(state, None)

    if auth is None:
        # check the state to avoid cross-site forgery
        return 'Invalid state!', 400
    # get the token (Token class)
    token = auth.request_token(code, state)

    # put serialized token in a session
    session['token'] = pickle.dumps(token)
    try:
        with spotify_tekore_client.token_as(token):
            current_user = spotify_tekore_client.current_user()
            user_id = current_user.id
            # put user's id in a session
            session['user'] = user_id
            user_entry = User.query.filter_by(spotify_id=user_id).first()
            if not user_entry:
                # if the user is not yet registered in db
                # save user to the db with the refresh token
                refresh_token = token.refresh_token
                user_entry = User(spotify_id=user_id, spotify_token=refresh_token)
                db.session.add(user_entry)
                db.session.commit()

    except tk.HTTPError:
        return None
    return redirect(url_for('main.home'), 307)


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
            top_tracks = spotify_tekore_client.current_user_top_tracks(limit=50)
            # current_user = spotify_tekore_client.current_user()
            # print(current_user.display_name)
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
                "artist_names": [artist_name] + utils.get_filtered_artist_names(artist_name),
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


@spotify.route("/check_spotify_login")
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
    # token = users.get(user, None)
    # token = session.get('access_token', None)

    if user is None or token is None:
        print('something is None')
        session.pop('user', None)
        # session.pop('access_token', None)
        session.pop('token', None)
        return None, None

    if token.is_expiring:
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
            user_image = current_user.images[0].url
    except tk.HTTPError:
        return None
    user_info = {
        "username": username,
        "user_image": user_image
    }
    return user_info


@spotify.route('/spotify_user_popup')
def spotify_user_popup():
    """
    :return:
    """
    user, token = check_spotify()
    if not user or not token:
        return None

    user_info = get_spotify_user_info(token)


@spotify.route('/fetch_album_id', methods=['POST'])
def spotify_fetch_album_id():
    content = request.get_json()
    if not content:
        return None
    album_name = content['album_name']
    artist_name = content['artist_name']
    album_id = spotify_get_album_id(album_name, artist_name)
    print(album_id)
    if not album_id:
        return make_response(jsonify(
            {'message': f"album id could not be found"}
        ),
            404)
    return jsonify({
        "album_id": album_id
    })


def spotify_get_album_id(album_name, artist_name):
    """
    gets Spotify album id with through Tekore
    :param album_name: album's title
    :param artist_name: artist's title
    :return: Spotify album id
    """
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
        except tk.HTTPError:
            return None
        if not album_info:
            return None
        print(len(album_info[0].items))
        album_items = album_info[0].items
        artist_name = artist_name.lower().replace(' & ', ' and ')
        album_name = album_name.lower()
        ratio_threshold = 94
        album_id_found = None
        for album in album_items:
            try:
                current_artist = album.artists[0].name. \
                    lower().replace(' & ', ' and ').replace('the ', '')
                current_album = utils.get_filtered_name(album.name)
                print('album to find:', album_name)
                print('filtered:', current_album)
                print(f'item: {current_artist}, {album.id}, {album.name}')
                print(fuzz.ratio(artist_name, current_artist))
                print('partial:', fuzz.partial_ratio(album_name, current_album))
                print('ratio album:', fuzz.ratio(album_name, current_album))
                # if fuzz.ratio(artist_name, current_artist) > 90:
                #     return album_id
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

# @spotify.after_request
# def add_header(r):
#     """
#     Add headers to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     """
#     print('after requestjke')
#     r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     r.headers["Pragma"] = "no-cache"
#     r.headers["Expires"] = "0"
#     r.headers['Cache-Control'] = 'public, max-age=0'
#     return r
