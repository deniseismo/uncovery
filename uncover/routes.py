from flask import render_template, request, jsonify, make_response, url_for

from uncover import app
from uncover.helpers.collage_creator import save_collage
from uncover.helpers.lastfm_api import lastfm_get_users_top_albums
from uncover.helpers.main import get_artists_top_albums_images, sql_select_artist_albums
from uncover.helpers.spotify_api import spotify_get_users_playlist_albums
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
    content = request.get_json()
    username = content['qualifier']
    time_period = content['option']
    if not username:
        # if the input's empty, send an error message and a 'failure' image
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': 'a user has no name, huh?',
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    albums = lastfm_get_users_top_albums(username, time_period=time_period)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"couldn't find {username}'s top albums; are you sure {username} is a username?",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    a_list_of_image_urls = [album['image'] for album in albums['albums']]
    collage_filename = save_collage(a_list_of_image_urls[:9])
    image_file = url_for('static', filename='collage/' + collage_filename)
    albums['collage'] = image_file
    return jsonify(albums)


@app.route("/by_artist", methods=["POST"])
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
    # a_list_of_image_urls = [
    #     url_for('static', filename='cover_art_images/' + os.path.basename(album['image']))
    #     for album in albums['albums']]
    # print(a_list_of_image_urls)
    # collage_filename = save_collage(a_list_of_image_urls[:9])
    # image_file = url_for('static', filename='collage/' + collage_filename)
    # albums['collage'] = image_file
    return jsonify(albums)


# def get_albums_by_artist():
#     """
#     gets artist's top albums
#     :return: jsonified dictionary {album_name: cover_art}
#     """
#     # input's value from the form
#     content = request.get_json()
#     artist = content["qualifier"]
#     if not artist:
#         # if the input's empty, send an error message and a 'failure' image
#         failure_art_filename = display_failure_art(get_failure_images())
#         return make_response(jsonify(
#             {'message': 'an artist has no name, huh?',
#              'failure_art': url_for('static',
#                                     filename=failure_art_filename)}
#         ),
#             404)
#     # get albums images
#     albums = get_artists_top_albums_images(artist)
#     if not albums:
#         # if the given username has no albums or the username's incorrect
#         failure_art_filename = display_failure_art(get_failure_images())
#         return make_response(jsonify(
#             {'message': f"couldn't find {artist}'s top albums; are you sure {artist} is an artist?",
#              'failure_art': url_for('static',
#                                     filename=failure_art_filename)}
#         ),
#             404)
#
#     a_list_of_image_urls = [url_for('static', filename='/cover_art_images/' + os.path.basename(album['image'])) for album in albums['albums']]
#     print(a_list_of_image_urls)
#     # collage_filename = save_collage(a_list_of_image_urls[:9])
#     # image_file = url_for('static', filename='collage/' + collage_filename)
#     # albums['collage'] = image_file
#     return jsonify(albums)


@app.route("/by_spotify", methods=["POST"])
def get_albums_by_spotify():
    """
    gets album cover art images based on Spotify's playlist
    :return: jsonified dictionary {album_name: cover_art}
    """
    # input's value from the form
    content = request.get_json()
    playlist_id = content["qualifier"]
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
    albums = spotify_get_users_playlist_albums(playlist_id)
    if not albums:
        # if the given username has no albums or the username's incorrect
        failure_art_filename = display_failure_art(get_failure_images())
        return make_response(jsonify(
            {'message': f"your playlist's kinda dumb",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    a_list_of_image_urls = [album['image'] for album in albums['albums']]
    collage_filename = save_collage(a_list_of_image_urls[:9])
    image_file = url_for('static', filename='collage/' + collage_filename)
    albums['collage'] = image_file
    return jsonify(albums)


@app.route("/save_collage")
def save_collage():
    """
    gets album pictures list to create a collage from
    :return: a URL to the saved collage
    """
    content = request.get_json()
    album_pictures = content['images']
    collage_filename = save_collage(album_pictures)
    image_file = url_for('static', filename='collage/' + collage_filename)
    return image_file



@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', title='Page Not Found'), 404

