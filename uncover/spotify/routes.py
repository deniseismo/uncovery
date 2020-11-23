import pickle

import tekore as tk
from flask import request, url_for, Blueprint, redirect, session, jsonify, make_response

from uncover import db
from uncover.models import User
from uncover.spotify.spotify_user_oauth import get_spotify_auth, spotify_get_album_id, check_spotify, \
    get_spotify_user_info

spotify = Blueprint('spotify', __name__)

spotify_tekore_client = tk.Spotify()


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


@spotify.route('/spotify_logout', methods=['GET'])
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
    album_id = None
    user, token = check_spotify()

    if user and token:
        user_info = get_spotify_user_info(token)
        try:
            country = user_info['country']
        except KeyError:
            country = None
        album_name = content['album_name']
        artist_name = content['artist_name']
        spotify_artist_name = content['spotify_artist_name']
        album_id = spotify_get_album_id(album_name, artist_name, spotify_artist_name, country)
        print(album_id)
        if not album_id:
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
        "album_id": album_id
    })
