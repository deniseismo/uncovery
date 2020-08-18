from flask import Flask


app = Flask(__name__)

from uncover import routes
from uncover import helpers
