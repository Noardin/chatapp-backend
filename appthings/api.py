from flask import Blueprint, send_from_directory
from flask_cors import cross_origin
from flask_restful import Api
from appthings.Resources_for_app import Messages, update_userData, Register,\
    ChangePassword, UpdateSettings, RequestPasswordChange, Login
from appthings.models import *

api = Blueprint('api',__name__)


@api.after_request # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


apps = Api(api)
apps.add_resource(Messages, '/Messages')
apps.add_resource(ChangePassword, '/change_password/<token>')
apps.add_resource(update_userData, '/update_userdata')
apps.add_resource(Login, '/login')
apps.add_resource(Register, '/registrate')
apps.add_resource(UpdateSettings, '/update_settings')
apps.add_resource(RequestPasswordChange, '/request_password_change')


@api.route('/confirm/<token>')
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def confirm_email(token):
    return User.confirm(token)

@api.route('/get/<file>')
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_image_by_URL(file):
    img = send_from_directory('static','img/profile_img/'+file)

    return img


@api.route('/get_audio/<file>')
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_audio_by_URL(file):
    img = send_from_directory('static','audio_messages/'+file )

    return img