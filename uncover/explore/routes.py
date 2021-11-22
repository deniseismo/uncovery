import json

from flask import request, url_for, Blueprint, make_response, jsonify

from uncover.explore.filter_albums import get_albums_by_filters
from uncover.utilities.failure_handlers import display_failure_art, get_failure_images

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
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"couldn't find any covers",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    albums = get_albums_by_filters(genres=genres, time_span=time_span, colors_list=colors)
    if not albums:
        # if no albums found, make a failure response
        failure_art_filename = display_failure_art(get_failure_images())
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
        with open('uncover/static/data/genres_list.json') as jsonfile:
            tags_list = json.load(jsonfile)
    except (IOError, OSError):
        tags_list = []
    try:
        search_query = request.get_json()['query']
    except (KeyError, TypeError, IndexError):
        search_query = ''
    filtered_tags_list = []
    # check if the input's not empty
    if search_query:
        if len(search_query) < 98:
            search_query = search_query.lower()
            for tag in tags_list:
                # if a 'tag' consists of the provided input, add it to the final list
                if search_query in tag:
                    filtered_tags_list.append(tag)
    suggestions = {"suggestions": filtered_tags_list}
    print(suggestions)
    return jsonify(suggestions)
