from flask import request, url_for, Blueprint, make_response, jsonify

from uncover.client.explore.filter_albums import get_albums_by_filters
from uncover.client.explore.filter_tags import get_suggested_tags
from uncover.utilities.failure_handlers import pick_failure_art_image

explore = Blueprint('explore', __name__)


@explore.route("/explore", methods=["POST"])
def get_album_cover_arts_by_filters():
    """
    get cover arts by user-defined filters
    :return: a jsonified dict with all the albums found
    """
    content = request.get_json()
    print(content)
    genres = None
    time_span = None
    colors = None
    try:
        genres = content['option']['genres']
    except KeyError:
        pass
    try:
        time_span = content['option']['time_span']
    except KeyError:
        pass
    try:
        colors = content['option']['colors']
    except KeyError:
        pass
    # gets albums
    print(type(genres), type(time_span))
    if not isinstance(genres, list) or not (isinstance(time_span, list)):
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': f"couldn't find any covers",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    albums = get_albums_by_filters(genres=genres, a_list_of_time_span_dates=time_span, colors_list=colors)
    if not albums:
        # if no albums found, make a failure response
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': f"couldn't find any covers",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    return jsonify(albums)


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
