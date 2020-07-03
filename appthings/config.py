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
    CORS_HEADERS = 'Content-Type'
    UPLOAD_FOLDER = join(dirname(realpath(__file__)), '../static/img/profile_img')
    UPLOAD_FOLDER_AUDIO = join(dirname(realpath(__file__)), '../static/audio_messages')
    UPLOAD_FOLDER_IMAGE_MESSAGE = join(dirname(realpath(__file__)), '../static/img/message_img')
    PASSWORD_CHANGE_KEY = 'asdfsdfsdf'
    SENDGRID_API_KEY = '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'

    SECURITY_PASSWORD_SALT = 'mujtajnyklic'
    DEFAULT_PROFILE_IMG ='icons8-person-90'
    DATABASE_URI = 'postgres+psycopg2://ehlkmkyqzanmve:7f24b930611d412d9f55729e5e89822c1261fb3230489abfdb044ec3a1ad2897@ec2-54-75-245-196.eu-west-1.compute.amazonaws.com:5432/df4efm94h7l0nf'