from flask import render_template, request, Blueprint, url_for, jsonify

from uncover.helpers.collage_creator import save_collage
from uncover.spotify.spotify_user_oauth import check_spotify, get_spotify_user_info

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    """
    renders home page
    """
    logged_in = False
    user_info = None
    user, token = check_spotify()
    if user and token:
        logged_in = True
        user_info = get_spotify_user_info(token.access_token)
    return render_template("home.html", logged_in=logged_in, user_info=user_info)


@main.route("/save_collage", methods=["POST"])
def get_collage():
    """
    gets album pictures list to create a collage from
    :return: a URL to the saved collage
    """
    content = request.get_json()
    album_pictures = content['images'][:9]
    print(album_pictures)
    collage_filename = save_collage(album_pictures)
    image_file = url_for('static', filename='collage/' + collage_filename)
    return jsonify(image_file)

# @main.after_request
# def add_header(r):
#     """
#     Add headers to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     """
#     print('after requestjke')
#     r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     r.headers["Pragma"] = "no-cache"
#     r.headers["Expires"] = "0"
#     r.headers['Cache-Control'] = 'public, max-age=0'
#     return r
