import pickle
import random

import tekore as tk
from flask import Blueprint, session, url_for, request, make_response, jsonify
from werkzeug.utils import redirect

from uncover import db
from uncover.models import User
from uncover.music_apis.spotify_api.spotify_album_handlers import get_spotify_album_info
from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client
from uncover.music_apis.spotify_api.spotify_user_handlers import get_spotify_auth, check_spotify, get_spotify_user_info, \
    spotify_get_users_albums
from uncover.utilities.failure_handlers import pick_failure_art_image

spotify = Blueprint('spotify', __name__)


@spotify.route("/spotify_login", methods=['GET'])
def spotify_login():
    """
    get an authorization url and redirects to the spotify login page
    :return: redirect url
    """
    auth = get_spotify_auth()
    # store a random state in a server-side cookie-session
    session['state'] = auth.state
    return redirect(auth.url, 307)


@spotify.route('/spotify_logout', methods=['POST'])
def spotify_logout():
    """
    logs user out
    :return: redirects to the home page
    """
    user = session.pop('user', None)
    return redirect(url_for('main.home'), 307)


@spotify.route("/spotify_callback", methods=["GET"])
def spotify_callback():
    """
    a function that gets triggered after the user successfully granted the permission
    :return:
    """
    print('spotify callback worked!')
    error = request.args.get('error', None)
    code = request.args.get('code', None)
    state = request.args.get('state', None)
    if error:
        return redirect(url_for('main.home'), 307)

    # get current user's state
    user_state = session.get('state', None)
    # check if it's there and equals to the state from the callback (against cross-site forgery)
    if user_state is None or user_state != state:
        return redirect(url_for('main.home'), 307)

    auth = get_spotify_auth()
    # get token object (Tekore token with access and refresh token inside)
    token = auth.request_token(code, auth.state)

    # put serialized token in a session
    session['token'] = pickle.dumps(token)
    spotify_tekore_client = get_spotify_tekore_client()
    try:
        with spotify_tekore_client.token_as(token):
            current_user = spotify_tekore_client.current_user()
            user_id = current_user.id
            # put user's id in a session
            session['user'] = user_id
            user_entry = User.query.filter_by(spotify_id=user_id).first()
            if not user_entry:
                print(f'new user! id: {user_id}')
                # if the user is not yet registered in db
                # save user to the db with the refresh token
                refresh_token = token.refresh_token
                user_entry = User(spotify_id=user_id, spotify_token=refresh_token)
                db.session.add(user_entry)
                db.session.commit()

    except tk.HTTPError:
        print('http error')
        return None
    return redirect(url_for('main.home'), 307)


@spotify.route('/fetch_album_id', methods=['POST'])
def spotify_fetch_album_id():
    content = request.get_json()
    if not content:
        return None
    user, token = check_spotify()

    if user and token:
        user_info = get_spotify_user_info(token)
        country = user_info.country
        album_name = content['album_name']
        artist_name = content['artist_name']
        spotify_artist_name = content['spotify_artist_name']
        album_info = get_spotify_album_info(
            album_name=album_name,
            artist_name=artist_name,
            spotify_artist_name=spotify_artist_name,
            token_based=True,
            country=country,
            token=token
        )
        if not album_info:
            return make_response(jsonify(
                {'message': f"album id could not be found"}
            ),
                404)
    else:
        return make_response(jsonify(
            {'message': f"no token or user provided"}
        ),
            403)
    return jsonify({
        "album_id": album_info.id
    })


@spotify.route("/by_spotify", methods=["POST"])
def get_albums_by_spotify():
    """
    gets album cover art images based on Spotify's playlist
    :return: jsonified dictionary {album_name: cover_art}
    """
    user, token = check_spotify()
    if not user or not token:
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': f"you are not logged in!",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            401)
    albums = spotify_get_users_albums(token)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': f"some things can't be uncovered",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    # shuffles a list of albums to get random results
    random.shuffle(albums["albums"])
    albums['albums'] = albums['albums'][:9]
    # adds ids to albums
    for count, album in enumerate(albums['albums']):
        album['id'] = count
    return jsonify(albums)
