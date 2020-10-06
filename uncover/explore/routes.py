import json

from flask import request, url_for, Blueprint, make_response, jsonify

from uncover.helpers.filter_albums import explore_filtered_albums
from uncover.helpers.main import sql_select_artist_albums, get_artists_top_albums_images
from uncover.helpers.utilities import display_failure_art, get_failure_images

explore = Blueprint('explore', __name__)


@explore.route("/by_artist", methods=["POST"])
def sql_get_albums_by_artist():
    """
    gets artist's top albums
    :return: jsonified dictionary {album_name: cover_art}
    """
    # input's value from the form
    content = request.get_json()
    artist = content["qualifier"]
    if not artist:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': 'an artist has no name, huh?',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    # get albums images
    albums = sql_select_artist_albums(artist)
    if not albums:
        albums = get_artists_top_albums_images(artist)
        # TODO: add saving data to db if it doesn't exist yet
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"couldn't find {artist}'s top albums; are you sure {artist} is an artist?",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    return jsonify(albums)


@explore.route("/explore", methods=["POST"])
def get_albums_by_filter():
    """
    :return:
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
    albums = explore_filtered_albums(genres=genres, time_span=time_span)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"couldn't find albums; try picking some other filters",
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
        # used for triggered the 'add' button whether the tag's in the list or not
        search_query = request.get_json()['query']

    filtered_tags_list = []
    for tag in tags_list:
        if search_query:
            if search_query in tag:
                filtered_tags_list.append(tag)

    suggestions = {"suggestions": filtered_tags_list}
    return jsonify(suggestions)