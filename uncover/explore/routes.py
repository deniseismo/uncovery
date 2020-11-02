import json

from flask import request, url_for, Blueprint, make_response, jsonify

from uncover.explore.filter_albums import explore_filtered_albums
from uncover.helpers.utilities import display_failure_art, get_failure_images

explore = Blueprint('explore', __name__)


@explore.route("/explore", methods=["POST"])
def get_albums_by_filter():
    """
    finds albums for specific filters (tags & time span)
    :return: a jsonified dict with all the albums found
    """
    content = request.get_json()
    print(content)
    genres = None
    time_span = None
    try:
        genres = content['option']['genres']
    except KeyError:
        pass
    try:
        time_span = content['option']['time_span']
    except KeyError:
        pass
    # gets albums
    albums = explore_filtered_albums(genres=genres, time_span=time_span)
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


@explore.route("/get_tags", methods=["POST", "GET"])
def get_tags_list():
    """
    gets a list of genres
    filtered based on the search query
    :return:
    """
    with open('uncover/static/data/genres_list.json') as jsonfile:
        tags_list = json.load(jsonfile)
    if request.method == "GET":
        # used for autocomplete/suggestions
        search_query = request.args.get('query')
    else:
        # used for triggering the 'add' button whether the tag's in the list or not
        search_query = request.get_json()['query']

    filtered_tags_list = []
    # check if the input's not empty
    if search_query:
        search_query = search_query.lower()
        for tag in tags_list:
            # if a 'tag' consists of the provided input, add it to the final list
            if search_query in tag:
                filtered_tags_list.append(tag)
    suggestions = {"suggestions": filtered_tags_list}
    return jsonify(suggestions)
