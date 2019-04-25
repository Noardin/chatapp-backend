from flask import Flask
from appthings.api import api
from flask_socketio import SocketIO
from flask_mail import Mail


socketio = SocketIO()
mailn = Mail()


def inicialize():
    app = Flask('rest_api', static_folder='/static')
    app.config.from_object('appthings.config.BaseConfig')
    socketio.init_app(app)
    mailn.init_app(app)

    app.register_blueprint(api, url_prefix='/api')

    return app
