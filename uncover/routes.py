import os
import json
from flask import render_template, request, redirect, url_for, jsonify
from uncover import app
from uncover.helpers import lookup_tags, get_top_albums, get_users_top_albums


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/by_username", methods=["POST"])
def get_top_albums():
    if request.method == "POST":
        username = request.form["username"]
        # tags = lookup_tags(artist)
        albums = get_users_top_albums(username)
        print(f'username is {username}')
        print(albums)
        print(f'jsonified albums are {jsonify(albums)}')
        return jsonify(albums)

