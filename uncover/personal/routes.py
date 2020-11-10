import random

from flask import request, Blueprint, jsonify, make_response, url_for

from uncover import cache
from uncover.helpers.lastfm_api import lastfm_get_users_top_albums, lastfm_get_user_avatar
from uncover.helpers.utilities import display_failure_art, get_failure_images
from uncover.spotify.spotify_user_oauth import spotify_get_users_albums, check_spotify

personal = Blueprint('personal', __name__)


@personal.route("/by_lastfm_username", methods=["POST"])
def get_albums_by_username():
    """
    gets user's top albums based on their last.fm stats
    :return: jsonified dictionary {album_name: cover_art}
    """
    # TODO: validator on input (e.g. not having spaces in the username)
    # input's values from the form
    content = request.get_json()
    username = content['qualifier']
    time_period = content['option']
    if not username:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': 'a user has no name, huh?',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    username = username.strip()
    if not (1 < len(username) < 16):
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': 'you are not fooling no one',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    if time_period == "shuffle":
        cache.delete_memoized(lastfm_get_users_top_albums, username=username, time_period='shuffle')
    albums = lastfm_get_users_top_albums(username, time_period=time_period)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"couldn't find any albums",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    return jsonify(albums)


@personal.route("/by_spotify", methods=["POST"])
def get_albums_by_spotify():
    """
    gets album cover art images based on Spotify's playlist
    :return: jsonified dictionary {album_name: cover_art}
    """
    user, token = check_spotify()
    if not user or not token:
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"you are not logged in!",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            401)
    albums = spotify_get_users_albums(token)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
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


@personal.route("/get_user_avatar", methods=["POST"])
def get_avatar_image():
    """
    gets user's avatar image
    :return: a jsonified dict with user avatar image url in it
    """
    try:
        content = request.get_json()
    except TypeError:
        return None
    if not content:
        return None
    try:
        username = content['qualifier']
    except (KeyError, IndexError, TypeError):
        return None
    if not username:
        return None
    user_avatar = lastfm_get_user_avatar(username)
    if not user_avatar:
        return None

    return jsonify({
        "avatar": user_avatar
    })
