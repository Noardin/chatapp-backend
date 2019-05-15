
from sqlalchemy import create_engine, ForeignKey, DateTime, Boolean
from sqlalchemy import Column, Date, Integer, String, column, exc, Table, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, column_property, mapper, aliased
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from appthings.hashes import verify_hash, set_hash
from flask_marshmallow import Marshmallow
from marshmallow import fields, Schema
import datetime
from appthings.token_for_email import generate_email_confirmation_token, confirm_token, generate_password_change_token, confirm_password_token
from sqlalchemy.orm import relationship, backref
from flask import url_for, render_template
from appthings.events import send_email
engine = create_engine('sqlite:///chat.db', echo=True)
session_ = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
ma = Marshmallow()
metadata = MetaData()
conn = engine.connect()

########################################################################
class User(Base):
    """"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    email = Column(String, unique=True, nullable=False)
    registered_on = Column(DateTime, nullable=False)
    admin = Column(Boolean, nullable=False, default=False)
    confirmed = Column(Boolean, nullable=False, default=False)
    confirmed_on = Column(DateTime, nullable=True)
    settings = relationship('Settings',back_populates='user', uselist=False)

    # ----------------------------------------------------------------------
    def __init__(self, username, password, email, confirmed, admin=False,  confirmed_on=None):
        """"""
        self.username = username
        self.password = set_hash(password)
        self.email = email
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.registered_on = datetime.datetime.now()

    def set_password(self, old_password, new_password):
        if not verify_hash(old_password, self.password):
            return False
        else:
            self.password = set_hash(new_password)
            return True

    @classmethod
    def authenticate(cls, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')

        if not username or not password:
            return None

        user = cls.getUserData(username)

        if not user or not verify_hash(password, user['password']):
            return None

        return user

    @classmethod
    def getUserData(cls, username):
        userdata = session_.query(User.username, User.confirmed, User.email,
                                  User.id,User.password, Settings.profile_img,
                                  Settings.nickname).join(Settings).filter(User.username == username).first()
        userdata = userSchema().dump(userdata).data
        return userdata

    @classmethod
    def register(cls, **data):
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        try:
            session_.commit()
            s = User(username=username, password=password, email=email, confirmed=Column.default)
            session_.add(s)
            session_.flush()
            user_id = s.id
            h = Settings(username=username, profile_img=Column.default, nickname=username, user_id=user_id)
            session_.add(h)
            token = generate_email_confirmation_token(email)
            confirm_url = url_for('api.confirm_email', token=token, _external=True)
            html = render_template('confirm_email_template.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            send_email(email, subject, html)
            return {'registrated': True}
        except exc.IntegrityError:
            session_.rollback()
            return {'registrated': False}


    @classmethod
    def confirm(cls, token):
        email = confirm_token(token)
        user = session_.query(User).filter_by(email=email).first()
        if not email or not user:

            msg = 'The confirmation link is invalid or has expired.'
            return render_template('activate_template.html', msg=msg)
        else:
            if user.confirmed:
                msg = 'your account has already been confirmed. Please login'
                return render_template('activate_template.html', msg=msg)
            else:
                user.confirmed = True
                user.confirmed_on = datetime.datetime.now()
                session_.add(user)
                session_.commit()
                msg = 'You have confirmed your account. Thanks!'
                return render_template('activate_template.html', msg=msg)


# ///////////////////////////////////////////////////////


class MessagesData(Base):
    __tablename__ = "messages_data"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    message = Column(String)
    date = Column(Date, nullable=False)
    audio = Column(Boolean)
    deleted = Column(Boolean, default=False)
    settings_id = Column(Integer, ForeignKey('settings.id'))
    settings = relationship('Settings')
    user = relationship('User')
    user_id = Column(Integer, ForeignKey(User.id))
    reaction = relationship('Reaction', uselist=False)

    def __init__(self, username, message, audio, settings_id, deleted, user_id):
        self.audio = audio
        self.username = username
        self.message = message
        self.date = datetime.date.today()
        self.settings_id = settings_id
        self.deleted = deleted
        self.user_id = user_id

    @classmethod
    def getALL(cls, user):
        dates = session_.query(MessagesData.date.distinct().label('date'))
        dates = [str(row.date) for row in dates.all()]
        print(dates)
        if not str(datetime.date.today()) in dates or len(dates) == 0:
            print('appending')
            dates.append(str(datetime.date.today()))
            print(dates)
        messages = session_.query(MessagesData, Settings.profile_img, Settings.nickname, MessagesData.message,
                                  MessagesData.username,
                                  MessagesData.id, MessagesData.date,
                                  MessagesData.audio,
                                  MessagesData.deleted, Reactions.reakce
                                  ).join(Settings).join(Reactions).order_by(cls.date).all()

        messages = MessagesSchema(many=True).dump(messages).data
        print(messages)
        for message in messages:
            message['reakce'] = {
                'like':message['reakce'].count('like'),
                'XD':message['reakce'].count('XD'),
                'angry':message['reakce'].count('angry')
            }
            if message['username'] == user.username:
                message['you'] = True
            else:
                message['you'] = False

        message_data = [{'date':datum, 'messages':[message for message in messages if message['date'] == datum]} for datum in dates]
        print(message_data)
        return message_data

    @classmethod
    def insertMSG(cls, **kwargs):
        msg = kwargs.get('message')
        username = kwargs.get('username')
        user_id = session_.query(User.id).filter(User.username == username).first()
        user_id = userSchema().dump(user_id).data.get('id')
        audio = kwargs.get('audio')
        settings_id = session_.query(User.id).filter_by(username=username).first()
        message = MessagesData(message=str(msg), username=str(username),
                               audio=bool(audio), settings_id=int(settings_id.id),
                               deleted=Column.default, user_id=user_id)
        session_.add(message)
        session_.flush()
        message_id = message.id
        session_.commit()
        userdata = User.getUserData(username)
        kwargs['msg_id'] = message_id
        kwargs['date'] = str(datetime.date.today())
        kwargs['email'] = userdata['email']
        kwargs['profile_img'] = userdata['profile_img']
        kwargs['nickname'] = userdata['nickname']
        kwargs['reakce'] = {'like': 0,
                            'XD': 0,
                            'angry': 0}
        return kwargs

    @classmethod
    def deletemsg(cls, **kwargs):
        msg_id = kwargs.get('id')
        try:
            msg = session_.query(cls).filter_by(id=msg_id)
            msg_data = MessagesSchema().dump(msg.first())
            msg.update({
                'deleted':True
            })
            session_.commit()
            return {'deleted':True, 'data':msg_data}
        except exc.IntegrityError:
            session_.rollback()
            return {'deleted':False}
    @classmethod
    def updatemsg(cls,**kwargs):
        msg_id = kwargs.get('id')
        newmsg = kwargs.get('message')

        try:
            msg = session_.query(cls).filter_by(id=msg_id)

            msg.update({
                'message':newmsg
            })
            msg_data = MessagesSchema().dump(msg.first())
            session_.commit()
            return {'updated':True, 'data':msg_data}
        except exc.IntegrityError:
            session_.rollback()
            return {'updated':False}


# /////////////////////////////////////////////


class Reactions(Base):
    __tablename__="reakce"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)
    msg_id = Column(Integer, ForeignKey(MessagesData.id))
    msg = relationship(MessagesData)
    reakce = Column(String)

    def __init__(self, user_id, msg_id, reakce):
        self.user_id = user_id
        self.msg_id = msg_id
        self.reakce = reakce

    @classmethod
    def updateReaction(cls, **kwargs):
        try:

            msg_id = kwargs['reakce'].get('id')
            user_id = session_.query(User.id).filter(User.username == kwargs['current_user'].username).first()
            user_id = userSchema().dump(user_id).data['id']

            myReaction = session_.query(cls).filter(cls.msg_id == msg_id, cls.user_id == user_id)
            if myReaction.count() > 0:
                myReaction.update({
                    'reakce': kwargs['changed']
                })

            else:
                newreakce = cls(user_id=user_id,msg_id=msg_id, reakce = kwargs['changed'])
                session_.add(newreakce)

            session_.commit()
            reakceData = session_.query(cls).filter(cls.msg_id == msg_id)
            msg = session_.query(MessagesData).filter(MessagesData.id == msg_id).first()
            msg = MessagesSchema().dump(msg).data
            reakce = {}
            druhyreakce = ['like', 'XD', 'angry']
            for druh in druhyreakce:
                reakce[druh] = reakceData.filter(cls.reakce == str(druh)).count()
            reakce['date'] = msg['date']
            return {'updated': True, 'reakce': reakce}
        except exc.IntegrityError:
            print(exc.IntegrityError)
            session_.rollback()
            return {'updated': False}


# ///////////////////////////////////////////////////////


class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_img = Column(String, default='icons8-person-90')
    nickname = Column(String)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, back_populates='settings')
    message = relationship(MessagesData, back_populates='settings')

    def __init__(self, username, profile_img, nickname, user_id):
        self.username = username
        self.profile_img = profile_img
        self.nickname = nickname
        self.user_id = user_id

    @classmethod
    def UpdateSettings(cls,**kwargs):
        username = kwargs.get('username')

        if 'nickname' in kwargs:
            nickname = kwargs.get('nickname')
            try:
                userid = session_.query(User.id).filter(User.username == username).first()
                userid = userSchema().dump(userid).data
                print(userid)
                userdata = session_.query(Settings)\
                    .filter(Settings.user_id == userid['id']).update({'nickname':nickname})
                print(userdata)
                print('updated')
                session_.commit()
                return {'changed': True}
            except exc.IntegrityError:
                session_.rollback()
                return {'changed': False}
        else:
            profile_img = kwargs.get('profile_img')
            try:
                userid = session_.query(User.id).filter(User.username == username).first()
                userid = userSchema().dump(userid).data
                print(userid)
                userdata = session_.query(Settings) \
                    .filter(Settings.user_id == userid['id']).update({'profile_img': profile_img})
                session_.commit()
                print(userdata)
                return {'changed': True}
            except exc.IntegrityError:
                session_.rollback()
                return {'changed': False}


class ReactionSchema(ma.Schema):
    id = fields.Integer()
    msg_id = fields.Integer()
    user_id = fields.Integer()
    reakce = fields.String()


class MessagesSchema(ma.Schema):
    id = fields.Integer()
    username = fields.String()
    message = fields.String()
    date = fields.Date()
    audio = fields.Boolean()
    profile_img = fields.String()
    nickname = fields.String()
    reakce = fields.List(fields.String())
    deleted = fields.Boolean()


class userSchema(ma.Schema):
    id = fields.Integer()
    username = fields.String()
    email = fields.String()
    nickname = fields.String()
    profile_img = fields.String()
    confirmed = fields.Boolean()
    password = fields.String()


Base.metadata.create_all(engine)