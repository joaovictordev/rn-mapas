from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, ALL

application = Flask(__name__)
application.config.from_object('config')

db = SQLAlchemy(application)
migrate = Migrate(application, db)

manager = Manager(application)
manager.add_command('db', MigrateCommand)

login_manager = LoginManager()
login_manager.init_app(application)


from application.models import tables
from application.controllers import default