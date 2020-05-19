from flask_restful import Resource
from flask import jsonify, render_template, request, current_app, make_response
import os, datetime, random, string, jwt, json, re, base64, time
from appthings.token_for_email import confirm_password_token, generate_password_change_token
from appthings.models import *
from flask_socketio import emit, SocketIO
from appthings.events import *
from functools import wraps, update_wrapper
from appthings import inicializApp



alert = {
        'version': 'login',
        'variant': 'warning',
        'text': ''
    }


def decodebase64andsaveasfile(data, druh, current_user):
    if druh == 'image':
        N_data = re.sub('^data:image/.+;base64,', '', data)
        decodedData = base64.b64decode(N_data)
        # rename file and save

        oldfilename = User.getUserData(current_user.username)
        print('oldfilename', str(oldfilename['profile_img']))
        oldpath = os.path.join(current_app.config['UPLOAD_FOLDER'], str(oldfilename['profile_img'] + '.jpg'))
        filename = ''.join([random.choice(string.ascii_letters + string.digits)
                            for n in range(5)]) + '_' + str(current_user.username) + '_profile_img'
        newpath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename + '.jpg')
        print(newpath)
        if not oldfilename['profile_img'] == current_app.config['DEFAULT_PROFILE_IMG'] and os.path.exists(oldpath):
            os.renames(oldpath, newpath)
        with open(newpath, 'wb') as f:
            f.write(decodedData)
            f.close()
        kwargs = {
            'username': current_user.username,
            'profile_img': filename
        }
        update = Settings.UpdateSettings(**kwargs)
        update['filename'] = filename
        return update

    else:
        N_data = re.sub('^data:audio/.+;base64,', '', data)
        decodedData = base64.b64decode(N_data)
        return_data = {}
        # rename file and save
        filename = ''.join([random.choice(string.ascii_letters + string.digits)
                            for n in range(30)]) + '_' + str(current_user.username) + '_audioMessage'

        newpath = os.path.join(current_app.config['UPLOAD_FOLDER_AUDIO'], filename + '.wav')
        unique = os.path.isfile(newpath)
        while unique:
            print(unique)
            filename = ''.join([random.choice(string.ascii_letters + string.digits)
                                for n in range(30)]) + '_' + str(current_user.username) + '_audioMessage'

            newpath = os.path.join(current_app.config['UPLOAD_FOLDER_AUDIO'], filename + '.wav')
            unique = os.path.isfile(newpath)

        with open(newpath, 'wb') as f:
            print('writing')
            f.write(decodedData)
            print('after')
            f.close()
            return_data['message'] = filename
        return return_data


def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '')
        auth_headers = auth_headers.split()
        print(auth_headers)

        invalid_msg = {
            'message': 'Invalid token. Registeration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }

        if len(auth_headers) != 1:
            print('delka', len(auth_headers))
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[0]
            print('token',token)
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            user = session_.query(User).filter_by(email=data['sub']).first()
            print(user.username)
            if not user:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401 # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError, Exception) as e:
            print('error',e)
            return jsonify(invalid_msg), 401

    return _verify


class ChangePassword(Resource):
    method_decorators = [token_required]

    def get(self, current_user, token):
        email = confirm_password_token(token)
        if not email:
            return jsonify({'authenticated': False})

        else:
            return jsonify({'authenticated': True, 'email': email})


class Login(Resource):
    def post(self):
            data = request.get_json()
            data = data['UserData']
            user = User.authenticate(**data)
            if user:
                if user['confirmed']:
                    token = jwt.encode({
                        'sub': user['email'],
                        'iat': datetime.datetime.utcnow(),
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=80)},
                        current_app.config['SECRET_KEY'])
                    user.pop('password')
                    return jsonify({'token': token.decode('UTF-8'), 'authenticated': True,
                                    'UserData': user})
                else:
                    alert['text'] = 'not_email'
                    return jsonify(
                        {'msg': 'pravdepodobne jsi si neoveril email', 'authenticated': False, 'alert': alert})

            else:
                alert['text'] = 'not_heslo'
                return jsonify({'msg': 'spatne heslo', 'authenticated': False, 'alert': alert})


class DeleteMessage(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.get_json()
        deleted = MessagesData.deletemsg(**data)
        inicializApp.socketio.emit('deletemsg', deleted, room='chatroom', broadcast=True)


class UpdateMessage(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.get_json()
        updated = MessagesData.updatemsg(**data)
        inicializApp.socketio.emit('updatemsg', updated, room='chatroom', broadcast=True)


class Messages(Resource):
    method_decorators = [token_required]

    def get(self, current_user):
        return jsonify(MessagesData.getALL(current_user))

    def post(self, current_user):
        data = request.get_json()

        if data['audio']:
            audio = data['message']
            print(audio)
            return_data = decodebase64andsaveasfile(audio, 'audio', current_user)
            data['message'] = return_data['message']

        data['username'] = current_user.username
        msg = MessagesData.insertMSG(**data)
        msg = json.dumps(msg)
        inicializApp.socketio.emit('my response', msg, room='chatroom', broadcast=True)
        return ''


class UpdateReactions(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.get_json()
        data['current_user'] = current_user
        update = Reactions.updateReaction(**data)
        if update['updated']:
            inicializApp.socketio.emit('updatereactions', update['reakce'], room='chatroom', broadcast=True)
            return 'updated'
        else:
            return 'failed'


class Register(Resource):
    def options(self):
        return{}

    def post(self):
        data = request.get_json()
        data = data['UserData']
        user = User.register(**data)

        if not user['registrated']:
            alert['text'] = 'not'
            print('not')
            return {'registrated': user['registrated'], 'alert':alert}
        else:
            alert['text'] = 'done'
            return {'registrated': user['registrated'], 'alert': alert}


class RequestPasswordChange(Resource):
    method_decorators = [token_required]

    def get(self, current_user):
        token = generate_password_change_token(current_user.email, current_app.config['PASSWORD_CHANGE_KEY'])
        confirm_url = 'https://chatfrontend.herokuapp.com/#/settings/change/' + token
        html = render_template('change_password_email.html', confirm_url=confirm_url)
        subject = "click if you want to change your password"
        send_email(current_user.email, subject, html)
        return 'done'


class UpdateSettings(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.get_json()
        print(data)
        if 'imageBase64' in data['UserData']:
            alert['version'] = 'profile_img'
            try:
                image_b64 = data['UserData']['imageBase64']
                update = decodebase64andsaveasfile(image_b64,'image', current_user)
                print('decoded')
                if update['changed']:
                    alert['text'] = 'success'
                    alert['variant']= 'success'
                    return jsonify({'update_data': {'profile_img': update['filename']}, 'alert': alert})
                else:
                    alert['text'] = 'warning'
                    return jsonify({'update_data': {}, 'alert': alert})
            except:
                alert['variant'] = 'warning'
                alert['text'] = 'warning'
                return jsonify({'update_data': {}, 'alert': alert})
        if 'nickname' in data['UserData']:
            alert['version'] = 'nickname'

            nickname = data['UserData']['nickname']
            kwargs = {
                'nickname':nickname,
                'username': current_user.username
            }
            update = Settings.UpdateSettings(**kwargs)
            if update['changed']:
                alert['variant'] = 'success'
                alert['text'] = 'success'
                return jsonify({'update_data': {'nickname': nickname}, 'alert': alert})
            else:
                alert['variant'] = 'warning'
                alert['text'] = 'warning'
                return jsonify({'update_data': {}, 'alert': alert})

        if 'password1' in data['UserData']:
            alert['version'] = 'password_change'
            try:
                print('user data', data['UserData'])
                old_password = data['UserData']['password_old']
                new_password = data['UserData']['password1']
                user = session_.query(User).filter(User.username == current_user.username).first()
                rewrite = user.set_password(old_password, new_password)
                if not rewrite:
                    alert['variant'] = 'warning'
                    alert['text'] = 'warning'
                    return jsonify({'update_data': {}, 'alert': alert})
                alert['variant'] = 'success'
                alert['text'] = 'success'
                return jsonify({'update_data': {}, 'alert': alert})
            except:
                alert['variant'] = 'warning'
                alert['text'] = 'warning'
                return jsonify({'update_data': {}, 'alert': alert})


class update_userData(Resource):
    method_decorators = [token_required]

    def get(self, current_user):
        userdata = User.getUserData(current_user.username)
        userdata.pop('password')
        return jsonify({'UserData': userdata})
