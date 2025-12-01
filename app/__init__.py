from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Ensure the instance folder exists
try:
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
except OSError:
    pass

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

# Initialize Admin (we will add views in routes or a separate file, but let's init here)
admin = Admin(app, name='Photography Blog', url='/')

from app import routes, models
