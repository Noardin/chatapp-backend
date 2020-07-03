from os.path import join, dirname, realpath


class BaseConfig(object):
    SECRET_KEY = 'my_secret_key'
    SQLALCHEMY_DATABASE_URI='sqlite:///chat.db'
    MAIL_DEFAULT_SENDER = 'chatapp.assistant@gmail.com'
    # email server
    MAIL_USERNAME = 'chatapp.assistant'
    CORS_HEADERS = 'Content-Type'
    UPLOAD_FOLDER = join(dirname(realpath(__file__)), '../static/img/profile_img')
    UPLOAD_FOLDER_AUDIO = join(dirname(realpath(__file__)), '../static/audio_messages')
    UPLOAD_FOLDER_IMAGE_MESSAGE = join(dirname(realpath(__file__)), '../static/img/message_img')
    PASSWORD_CHANGE_KEY = 'asdfsdfsdf'


    SECURITY_PASSWORD_SALT = 'mujtajnyklic'
    DEFAULT_PROFILE_IMG ='icons8-person-90'
