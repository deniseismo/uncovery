from dataclasses import asdict

from flask import request, url_for, Blueprint, make_response, jsonify

from uncover import cache
from uncover.album_processing.album_processing_helpers import make_album_covers_response
from uncover.client.musician.musician_handlers import fetch_artists_top_albums_images, sql_select_artist_albums
from uncover.music_apis.lastfm_api.lastfm_artist_handlers import lastfm_get_artist_correct_name
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

    correct_name = lastfm_get_artist_correct_name(artist)
    if correct_name:
        # corrects the name if there is need
        artist = correct_name
    artist_albums = sql_select_artist_albums(artist, sorting)
    if not artist_albums:
        print('this worked!')
        artist_albums = fetch_artists_top_albums_images(artist, sorting)
        # TODO: add saving data to db if it doesn't exist yet
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
        info_query=artist
    )
    return jsonify(album_covers_response)
