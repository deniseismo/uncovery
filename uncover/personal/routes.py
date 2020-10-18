from flask import request, Blueprint, jsonify, make_response, url_for

from uncover.helpers.lastfm_api import lastfm_get_users_top_albums, lastfm_get_user_avatar
from uncover.helpers.spotify_api import spotify_get_users_playlist_albums
from uncover.helpers.utilities import display_failure_art, get_failure_images

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
    if len(username) > 15 or len(username) < 2:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': 'this aint legal!',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    albums = lastfm_get_users_top_albums(username, time_period=time_period)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"couldn't find {username}'s top albums; are you sure {username} is a username?",
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
    # input's value from the form
    content = request.get_json()
    playlist_id = content["qualifier"]
    if not playlist_id:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': "your playlist's id looks kinda empty to me",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    # gets albums info through spotify's api based on playlist's id
    albums = spotify_get_users_playlist_albums(playlist_id)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"your playlist's kinda dumb",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    return jsonify(albums)


@personal.route("/get_user_avatar", methods=["POST"])
def get_avatar_image():
    """
    gets user's avatar image
    :return: a jsonified dict with user avatar image url in it
    """
    content = request.get_json()
    if not content:
        return None
    username = content['qualifier']
    if not username:
        return None
    user_avatar = lastfm_get_user_avatar(username)
    if not user_avatar:
        return None

    return jsonify({
        "avatar": user_avatar
    })
