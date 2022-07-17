from flask import request, url_for, Blueprint, make_response, jsonify

from uncover import cache
from uncover.client.musician.musician_handlers import fetch_artists_top_albums_images, sql_select_artist_albums
from uncover.utilities.failure_handlers import pick_failure_art_image

musician = Blueprint('musician', __name__)


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
    if not artist or not sorting:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': 'an artist has no name, huh?',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    if not isinstance(artist, str):
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': 'an artist has no name, huh?',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    if len(artist) > 98:
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': "you ain't foolin' no one",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    artist = artist.strip()
    # get albums images
    if sorting == "shuffle":
        cache.delete_memoized(sql_select_artist_albums, artist_name=artist, sorting='shuffle')
    albums = sql_select_artist_albums(artist, sorting)
    if not albums:
        print('this worked!')
        albums = fetch_artists_top_albums_images(artist, sorting)
        # TODO: add saving data to db if it doesn't exist yet
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': f"couldn't find any covers",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    return jsonify(albums)