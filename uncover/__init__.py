from flask import Flask
from flask_caching import Cache
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from uncover.config import Config

sess = Session()
db = SQLAlchemy()
# cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/tmp'})
cache = Cache(config={'CACHE_TYPE': 'simple'})


def create_app(config_class=Config):
    """
    creates an instance of an app
    :param config_class: Config class file with all the configuration
    :return: app
    """
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app = Flask(__name__)

    app.config.from_object(Config)
    cache.init_app(app)
    # pass the app to the database (initialize the app)
    db.init_app(app)
    sess.init_app(app)

    from uncover.profile.lastfm.routes import lastfm_profile
    from uncover.musician.routes import musician
    from uncover.explore.routes import explore
    from uncover.main.routes import main
    from uncover.errors.handlers import errors
    from uncover.profile.spotify.routes import spotify

    # register all blueprints
    app.register_blueprint(lastfm_profile)
    app.register_blueprint(explore)
    app.register_blueprint(main)
    app.register_blueprint(musician)
    app.register_blueprint(errors)
    app.register_blueprint(spotify)

    return app
