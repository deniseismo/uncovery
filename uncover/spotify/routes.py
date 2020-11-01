import random

import tekore as tk
from flask import current_app
from flask import request, url_for, Blueprint, redirect, session

import uncover.helpers.utilities as utils

spotify = Blueprint('spotify', __name__)

spotify_tekore_client = tk.Spotify()

auths = {}  # Ongoing authorisations: state -> UserAuth
users = {}  # User tokens: state -> token (use state as a user ID)


def get_spotify_oauth():
    scope = "user-library-read user-read-private user-top-read"
    # spotify_oauth = oauth2.SpotifyOAuth(
    #     client_id=current_app.config['SPOTIPY_CLIENT_ID'],
    #     client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
    #     redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'],
    #     scope=scope
    # )
    auth_url = f'{"https://accounts.spotify.com"}/authorize?client_id={current_app.config["SPOTIPY_CLIENT_ID"]}&client_secret={current_app.config["SPOTIPY_CLIENT_SECRET"]}&response_type=code&redirect_uri={current_app.config["SPOTIPY_REDIRECT_URI"]}&scope={scope}'
    return auth_url


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
    scope = tk.scope.user_top_read
    auth = tk.UserAuth(cred, scope)
    auths[auth.state] = auth
    return redirect(auth.url, 307)


@spotify.route("/spotify_callback", methods=["GET"])
def spotify_callback():
    """
    a function that gets triggered after the user successfully logged in to spotify
    :return:
    """
    code = request.args.get('code', None)
    state = request.args.get('state', None)
    print(f'state {state}')
    auth = auths.pop(state, None)

    if auth is None:
        return 'Invalid state!', 400

    token = auth.request_token(code, state)
    session['user'] = state
    # session['token'] = token
    users[state] = token
    return redirect(url_for('main.home'), 307)


def spotify_get_users_albums():
    """
    :param playlist_id: spotify's playlist ID or a playlist's URL
    :return: a dict {album_title: album_image_url}
    """

    # print('a new spotify function worked!')
    # user = session.get('user', None)
    # token = users.get(user, None)
    # # token = session.get('token', None)
    # print(f'user: {user}')
    # print(f'token: {token}')
    # # Return early if no login or old session
    # if user is None or token is None:
    #     print('something is None')
    #     session.pop('user', None)
    #     return None
    #
    # if token.is_expiring:
    #     print('token is expiring')
    #     conf = (
    #         current_app.config['SPOTIPY_CLIENT_ID'],
    #         current_app.config['SPOTIPY_CLIENT_SECRET'],
    #         current_app.config['SPOTIPY_REDIRECT_URI']
    #     )
    #     cred = tk.Credentials(*conf)
    #     token = cred.refresh(token)
    #     users[user] = token

    user, token = check_spotify()
    print(dir(token))
    print(type(token))
    print(token.refresh_token)
    print(f"user: {user}")
    print(f"token: {token}")
    if not user or not token:
        print('no user or no token present')
        return None

    try:
        with spotify_tekore_client.token_as(token):
            top_tracks = spotify_tekore_client.current_user_top_tracks()
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
                "rating": track.popularity
            }
            an_album_dict["artist_names"] = list(set(an_album_dict["artist_names"]))
            an_album_dict['names'] = list(set(an_album_dict['names']))
            # filter duplicates:
            if filtered_title not in list_of_titles:
                # append a title to a set of titles
                list_of_titles.add(filtered_title)
                # adds an album info only if a title hasn't been seen before
                album_info["albums"].append(an_album_dict)
    # shuffles a list of albums to get random results
    random.shuffle(album_info["albums"])
    # adds ids to albums
    for count, album in enumerate(album_info['albums']):
        album['id'] = count
    return album_info


@spotify.route("/check_spotify_login")
def check_spotify():
    """
    checks if the person's logged in the token's not expired
    refreshes token if present
    :return: (user, token)
    """
    user = session.get('user', None)
    token = users.get(user, None)
    if user is None or token is None:
        print('something is None')
        session.pop('user', None)
        return None, None

    if token.is_expiring:
        print('token is expiring')
        conf = (
            current_app.config['SPOTIPY_CLIENT_ID'],
            current_app.config['SPOTIPY_CLIENT_SECRET'],
            current_app.config['SPOTIPY_REDIRECT_URI']
        )
        cred = tk.Credentials(*conf)
        token = cred.refresh(token)
        users[user] = token

    return user, token

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
