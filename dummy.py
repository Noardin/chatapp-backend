from appthings.model import User, session_, Settings
from sqlalchemy import Column

user = User(username='newuser', password='ahoj', email='ahoj', confirmed=Column.default)
session_.add(user)
session_.flush()
user_id = user.id
user2 = Settings(username='newuser', nickname='ahoj', profile_img='sdfsdf', user_id=user_id)
session_.add(user2)
session_.commit()