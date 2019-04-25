from os.path import join, dirname, realpath


class BaseConfig(object):
    SECRET_KEY = 'my_secret_key'
    SQLALCHEMY_DATABASE_URI='sqlite:///chat.db'
    MAIL_DEFAULT_SENDER = 'triksiand@gmail.com'
    # email server
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'triksiand'
    MAIL_PASSWORD = 'Nobodyknows223355'
    CORS_HEADERS = 'Content-Type'
    UPLOAD_FOLDER = join(dirname(realpath(__file__)), '../static/img/profile_img')
    UPLOAD_FOLDER_AUDIO = join(dirname(realpath(__file__)), '../static/audio_messages')
    PASSWORD_CHANGE_KEY = 'asdfsdfsdf'
    SECURITY_PASSWORD_SALT = 'mujtajnyklic'