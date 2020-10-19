from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

from uncover.config import Config

db = SQLAlchemy()

cache = Cache(config={'CACHE_TYPE': 'simple'})


def create_app(config_class=Config):
    """
    creates an instance of an app
    :param config_class: Config class file with all the configuration
    :return: app
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    cache.init_app(app)
    # pass the app to the database (initialize the app)
    db.init_app(app)

    from uncover.personal.routes import personal
    from uncover.musician.routes import musician
    from uncover.explore.routes import explore
    from uncover.main.routes import main

    # register all blueprints
    app.register_blueprint(personal)
    app.register_blueprint(explore)
    app.register_blueprint(main)
    app.register_blueprint(musician)

    return app
