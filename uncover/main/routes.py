from flask import render_template, request, Blueprint, url_for, jsonify

from uncover.cover_art_collage.collage_handlers import save_collage
from uncover.music_apis.spotify_api.spotify_user_handlers import check_spotify, get_spotify_user_info

main = Blueprint('main', __name__)


@main.route("/", methods=["GET", "POST"])
@main.route("/home", methods=["GET", "POST"])
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


@main.route('/static/')
def forbid_static():
    return render_template('404.html', title='Page Not Found'), 404
