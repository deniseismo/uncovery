from flask import render_template, request, Blueprint, url_for, jsonify

from uncover.helpers.collage_creator import save_collage

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    """
    renders home page
    """
    return render_template("home.html")


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
