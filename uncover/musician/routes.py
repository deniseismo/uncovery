from flask import request, url_for, Blueprint, make_response, jsonify

import uncover.helpers.utilities as utils
from uncover.helpers.main_async import fetch_artists_top_albums_images, sql_select_artist_albums
from uncover.helpers.utilities import display_failure_art, get_failure_images

musician = Blueprint('musician', __name__)


@utils.timeit
@musician.route("/by_artist", methods=["POST"])
def get_albums_by_artist():
    """
    gets artist's top albums
    :return: jsonified dictionary {album_name: cover_art}
    """
    # input's value from the form
    content = request.get_json()
    artist = content["qualifier"]
    sorting = content["option"]
    print(f'getting {artist}')
    print(f'sorting: {sorting}')
    if not artist:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': 'an artist has no name, huh?',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    artist = artist.strip()
    # get albums images
    albums = sql_select_artist_albums(artist, sorting)
    if not albums:
        print('this worked!')
        albums = fetch_artists_top_albums_images(artist, sorting)
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
