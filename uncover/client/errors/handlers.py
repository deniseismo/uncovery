from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    """
    :return: a 404 page
    """
    return render_template('404.html', title='Page Not Found'), 404


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('404.html', title='Something Not Found'), 403


@errors.app_errorhandler(500)
def error_500(error):
    return render_template('404.html', title="Server's Down or Something"), 500


@errors.route('/static/')
def forbid_static():
    return render_template('404.html', title='Page Not Found'), 404
