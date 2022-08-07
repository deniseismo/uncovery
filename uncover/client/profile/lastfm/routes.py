from flask import Blueprint, request, make_response, jsonify, url_for

from uncover.album_processing.album_processing_helpers import make_album_covers_response
from uncover.music_apis.lastfm_api.lastfm_user_handlers import lastfm_get_users_top_albums, lastfm_get_user_avatar
from uncover.utilities.failure_handlers import pick_failure_art_image
from uncover.utilities.validation.exceptions.validation_exceptions import LastFMUserInputError
from uncover.utilities.validation.user_input_validation import validate_lastfm_user_input

lastfm_profile = Blueprint('lastfm_profile', __name__)


@lastfm_profile.route("/by_lastfm_username", methods=["POST"])
def get_albums_by_lastfm_username():
    """
    gets user's top albums based on their last.fm stats
    :return: jsonified dictionary {album_name: cover_art}
    """
    user_input = request.get_json()
    try:
        valid_user_input = validate_lastfm_user_input(user_input)
        username = valid_user_input.username
        time_period = valid_user_input.time_period
    except LastFMUserInputError as e:
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': str(e),
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    # if time_period == "shuffle":
    #     cache.delete_memoized(lastfm_get_users_top_albums, username=username, time_period='shuffle')
    lastfm_user_albums_info = lastfm_get_users_top_albums(username, time_period=time_period)
    if not lastfm_user_albums_info:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': f"couldn't find any albums",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    lastfm_user_albums, username_corrected = lastfm_user_albums_info
    album_covers_response = make_album_covers_response(
        info_type="user",
        info_query=username_corrected,
        albums=lastfm_user_albums
    )
    return jsonify(album_covers_response)


@lastfm_profile.route("/get_user_avatar", methods=["POST"])
def get_lastfm_user_avatar():
    """
    gets user's avatar on last.fm
    :return: a jsonified dict {"avatar": user_avatar} with the lastfm avatar
    """
    try:
        content = request.get_json()
    except TypeError:
        return None
    if not content:
        return None
    try:
        username = content['qualifier']
    except KeyError:
        return None
    if not username:
        return None
    user_avatar = lastfm_get_user_avatar(username)
    if not user_avatar:
        return None

    return jsonify({
        "avatar": user_avatar
    })
