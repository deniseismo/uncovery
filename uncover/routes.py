from flask import render_template, request, jsonify, make_response, url_for

from uncover import app
from uncover.helpers.discogs_api import get_artist_top_albums_images_via_discogs
from uncover.helpers.lastfm_api import get_users_top_albums
from uncover.helpers.spotify_api import get_albums_by_playlist
from uncover.helpers.utils import display_failure_art
from uncover.info import get_failure_images


@app.route("/")
@app.route("/home")
def home():
    """
    renders home page
    """
    return render_template("home.html")


@app.route("/by_username", methods=["POST"])
def get_albums_by_username():
    """
    gets user's top albums based on their last.fm stats
    :return: jsonified dictionary {album_name: cover_art}
    """
    # TODO: validator on input (e.g. not having spaces in the username)
    # input's values from the form
    username = request.form["qualifier"]
    time_period = request.form["option"]
    if not username:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': 'a user has no name, huh?',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    albums = get_users_top_albums(username, time_period=time_period)
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


@app.route("/by_artist", methods=["POST"])
def get_albums_by_artist():
    """
    gets artist's top albums
    :return: jsonified dictionary {album_name: cover_art}
    """
    # input's value from the form
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

    # albums = get_artists_top_albums_via_lastfm(artist)  # through lastfm api
    # albums = get_artists_top_albums_images_via_mb(artist)  # through musicbrainz
    # albums = get_artists_top_albums_images_via_spotify(artist) # through Spotify
    albums = get_artist_top_albums_images_via_discogs(artist)  # through Discogs
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"couldn't find {artist}'s top albums; are you sure {artist} is an artist?",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    # slicing the dictionary to make it 9 albums long
    # albums["albums"] = dict(itertools.islice(albums["albums"].items(), 9))
    return jsonify(albums)


@app.route("/by_spotify", methods=["POST"])
def get_albums_by_spotify():
    """
    gets album cover art images based on Spotify's playlist
    :return: jsonified dictionary {album_name: cover_art}
    """
    # input's value from the form
    playlist_id = request.form["qualifier"]
    if not playlist_id:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': "your playlist's id looks kinda empty to me",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    # gets albums info through spotify's api based on playlist's id
    albums = get_albums_by_playlist(playlist_id)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"your playlist's kinda dumb",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    return jsonify(albums)
