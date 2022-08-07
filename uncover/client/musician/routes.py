from flask import request, url_for, Blueprint, make_response, jsonify

from uncover import cache
from uncover.album_processing.album_processing_helpers import make_album_covers_response
from uncover.client.musician.musician_handlers import fetch_artists_top_albums_images, get_artist_albums_from_database
from uncover.music_apis.lastfm_api.lastfm_artist_handlers import lastfm_get_artist_correct_name
from uncover.utilities.failure_handlers import pick_failure_art_image
from uncover.utilities.validation.exceptions.validation_exceptions import ArtistUserInputError
from uncover.utilities.validation.user_input_validation import validate_artist_user_input

musician = Blueprint('musician', __name__)


@musician.route("/by_artist", methods=["POST"])
def get_albums_by_artist():
    """
    gets artist's top albums (or sorted as per user's request)
    :return: jsonified dictionary {"album_name": cover_art}
    """
    # input's value from the form
    user_input = request.get_json()
    try:
        valid_user_input = validate_artist_user_input(user_input)
        artist_name = valid_user_input.artist_name
        sorting = valid_user_input.sorting
    except ArtistUserInputError as e:
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': str(e),
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    # get albums images
    if sorting == "shuffle":
        cache.delete_memoized(get_artist_albums_from_database, artist_name=artist_name, sorting='shuffle')

    correct_name = lastfm_get_artist_correct_name(artist_name)
    if correct_name:
        # corrects the name if there is need
        artist_name = correct_name
    artist_albums = get_artist_albums_from_database(artist_name, sorting)
    if not artist_albums:
        artist_albums = fetch_artists_top_albums_images(artist_name, sorting)
    if not artist_albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': f"couldn't find any covers",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    album_covers_response = make_album_covers_response(
        albums=artist_albums,
        info_type="artist",
        info_query=artist_name
    )
    return jsonify(album_covers_response)
