import os
import time
import requests
import requests_cache
import json
from flask import render_template, request, redirect, url_for
from uncover import app
from uncover.helpers import lookup_tags, get_top_albums, get_users_top_albums


@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
def home():
    tags = ''
    if request.method == "POST":
        if not request.form["artist"]:
            print("must provide artist")
        else:
            artist = request.form["artist"]
            # tags = lookup_tags(artist)
            albums = get_users_top_albums(artist)
            print(tags)
            print(os.environ.get("API_KEY"))
            print(os.environ.get('USER_AGENT'))
            return render_template("home.html", albums=albums)

    return render_template("home.html", tags=tags)


@app.route("/about", methods=['GET', 'POST'])
def about():
    title = "About"
    return render_template("about.html", title=title)