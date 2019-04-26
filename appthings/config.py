from os.path import join, dirname, realpath


class BaseConfig(object):
    SECRET_KEY = 'my_secret_key'
    SQLALCHEMY_DATABASE_URI='sqlite:///chat.db'
    MAIL_DEFAULT_SENDER = 'chatapp.assistant@gmail.com'
    # email server
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'chatapp.assistant'
    MAIL_PASSWORD = 'Mn_sXn88'
    CORS_HEADERS = 'Content-Type'
    UPLOAD_FOLDER = join(dirname(realpath(__file__)), '../static/img/profile_img')
    UPLOAD_FOLDER_AUDIO = join(dirname(realpath(__file__)), '../static/audio_messages')
    PASSWORD_CHANGE_KEY = 'asdfsdfsdf'
    SECURITY_PASSWORD_SALT = 'mujtajnyklic'