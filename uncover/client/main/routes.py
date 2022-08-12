from flask import render_template, request, Blueprint, url_for, jsonify, make_response

from uncover.cover_art_collage.collage_handlers import save_collage
from uncover.music_apis.spotify_api.spotify_user_handlers import authenticate_spotify_user, get_spotify_user_info
from uncover.utilities.failure_handlers import pick_failure_art_image

main = Blueprint('main', __name__)


@main.route("/", methods=["GET", "POST"])
@main.route("/home", methods=["GET", "POST"])
def home():
    """
    renders home page
    """
    logged_in = False
    user_info = None
    user, token = authenticate_spotify_user()
    if user and token:
        logged_in = True
        user_info = get_spotify_user_info(token.access_token)
    return render_template("home.html", logged_in=logged_in, user_info=user_info)


@main.route("/save_collage", methods=["POST"])
def get_collage():
    """
    create collage from cover art images → get collage url
    :return: a URL to the saved collage
    """
    content = request.get_json()
    cover_art_urls = content['images'][:9]
    collage_filename = save_collage(cover_art_urls)
    if not collage_filename:
        failure_art_filename = pick_failure_art_image()
        return make_response(jsonify(
            {'message': f"could not create collage",
             'failure_art': url_for('static',
                                    filename=failure_art_filename)}
        ),
            404)
    collage_url = url_for('static', filename='collage/' + collage_filename)
    return jsonify(collage_url)


@main.route('/static/')
def forbid_static():
    return render_template('404.html', title='Page Not Found'), 404
