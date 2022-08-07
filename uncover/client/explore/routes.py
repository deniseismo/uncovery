from flask import request, url_for, Blueprint, make_response, jsonify

from uncover.album_processing.album_processing_helpers import make_album_covers_response
from uncover.client.explore.filter_albums import get_albums_by_filters
from uncover.client.explore.filter_tags import get_suggested_tags
from uncover.utilities.failure_handlers import pick_failure_art_image
from uncover.utilities.validation.exceptions.validation_exceptions import ExploreFiltersUserInputError
from uncover.utilities.validation.user_input_validation import validate_explore_filters_user_input

explore = Blueprint('explore', __name__)


@explore.route("/explore", methods=["POST"])
def get_album_cover_arts_by_filters():
    """
    get cover arts by user-defined filters
    :return: a jsonified dict with all the albums found
    """
    user_input = request.get_json()
    try:
        valid_user_input = validate_explore_filters_user_input(user_input)
        genres = valid_user_input.genres
        time_span = valid_user_input.time_span
        colors = valid_user_input.colors
    except ExploreFiltersUserInputError as e:
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': str(e),
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    albums_by_user_filters = get_albums_by_filters(
        genres=genres,
        a_list_of_time_span_dates=time_span,
        colors_list=colors
    )
    if not albums_by_user_filters:
        # if no albums found, make a failure response
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': f"couldn't find any covers",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    album_covers_response = make_album_covers_response(
        albums=albums_by_user_filters,
        info_type="explore",
        info_query=""
    )
    return jsonify(album_covers_response)


@explore.route("/get_tags", methods=["POST"])
def get_tags_list():
    """
    gets a list of genres
    filtered based on the search query
    :return:
    """
    try:
        search_query = request.get_json()['query']
    except (KeyError, TypeError):
        return None
    filtered_tags_list = get_suggested_tags(search_query)
    suggestions = {"suggestions": filtered_tags_list}
    print(suggestions)
    return jsonify(suggestions)
