from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from appthings.models import Base
from appthings.inicializApp import inicialize


app = inicialize()

migrate = Migrate(app, Base)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()