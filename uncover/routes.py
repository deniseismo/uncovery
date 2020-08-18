from flask import render_template
from uncover import app


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/about", methods=['GET', 'POST'])
def about():
    title = "About"
    return render_template("about.html", title=title)