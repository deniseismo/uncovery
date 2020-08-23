from flask import render_template, request, jsonify, make_response, url_for
from uncover import app
from uncover.helpers.lastfm_api import get_users_top_albums, get_artists_top_albums_via_lastfm
from uncover.utils import display_failure_art
from uncover.info import get_failure_images


@app.route("/")
@app.route("/home")
def home():
    """
    renders home page
    """
    return render_template("home.html")


@app.route("/by_username", methods=["POST"])
def get_top_albums():
    """
    gets user's top albums based on their last.fm stats
    :return: jsonified dictionary {album_name: cover_art}
    """
    username = request.form["qualifier"]
    if not username:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': 'a user has no name, huh?',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    albums = get_users_top_albums(username)
    # artists_albums = get_artists_albums_pictures(username)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"couldn't find {username}'s top albums; are you sure {username} is a username?",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    return jsonify(albums)
    # return jsonify(artists_albums)


@app.route("/by_artist", methods=["POST"])
def get_top_albums_by_artist():
    artist = request.form["qualifier"]
    if not artist:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': 'an artist has no name, huh?',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    albums = get_artists_top_albums_via_lastfm(artist)
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
