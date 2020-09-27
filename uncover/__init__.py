from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# dicts passed to 'jsonify()' don't get reordered
app.config['SERVER_NAME'] = '192.168.1.62:5000'
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uncover.db'

db = SQLAlchemy(app)


from uncover import routes
from uncover import helpers
from uncover import models
