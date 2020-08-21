from flask import Flask


app = Flask(__name__)
# dicts passed to 'jsonify()' don't get reordered
app.config['JSON_SORT_KEYS'] = False

from uncover import routes
from uncover import helpers
