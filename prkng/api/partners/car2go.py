from prkng.api import auth_required, create_token
from prkng.models import Carshares

import datetime
from flask import current_app, jsonify, Blueprint, request, send_from_directory
import os


car2go = Blueprint('car2go', __name__, url_prefix='/car2go')

def init_car2go(app):
    """
    Initialize login manager extension into flask application
    """
    app.register_blueprint(car2go)


@car2go.route('/', defaults={'path': None})
@car2go.route('/<path:path>')
def test_view(path):
    """
    Serve car2go interface.
    Should only be used for testing; otherwise serve with NGINX instead.
    """
    if path and not path.startswith(("assets", "public", "fonts", "images")):
        path = None
    sdir = os.path.dirname(os.path.realpath(__file__))
    if path and path.startswith("images"):
        sdir = os.path.abspath(os.path.join(sdir, '../../../../prkng-car2go/public'))
    else:
        sdir = os.path.abspath(os.path.join(sdir, '../../../../prkng-car2go/dist'))
    return send_from_directory(sdir, path or 'index.html')


@car2go.route('/api/token', methods=['POST'])
def generate_token():
    """
    Generate a JSON Web Token for use with Ember.js admin
    """
    data = request.get_json()
    uname, passwd = data.get("username"), data.get("password")
    if uname in current_app.config["CAR2GO_ACCTS"] \
    and passwd == current_app.config["CAR2GO_ACCTS"][uname]["password"]:
        with open(os.path.join(os.path.expanduser('~'), 'log', 'car2go_access.log'), 'a') as f:
            f.write('[LOGIN] User {} at {} with IP {}\n'.format(uname, datetime.datetime.now().isoformat(),
                request.environ['REMOTE_ADDR']))
        return jsonify(token=create_token(uname, ext=current_app.config["CAR2GO_ACCTS"][uname]["city"]))
    else:
        return jsonify(message="Username or password incorrect"), 401


@car2go.route('/api/cars', methods=['GET'])
@auth_required()
def get_checkins():
    """
    Get all car2go checkins
    """
    city = request.args.get('city', 'montreal')
    cars = Carshares.get_all('car2go', city)
    return jsonify(cars=cars), 200
