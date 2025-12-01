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
    # Create 'instance' in the application root (where app.py/run.py usually is, or relative to the package)
    # Since we are in app/__init__.py, app.root_path points to .../app
    # We want the instance folder to be at the same level as 'app' folder in the container structure (/app/instance)
    # But Flask default instance path is usually /app/instance if app is a package.
    # Let's just ensure the directory from the config is created if possible, or just create 'instance' in CWD.
    if not os.path.exists('instance'):
        os.makedirs('instance')
except OSError:
    pass

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

# Initialize Admin (we will add views in routes or a separate file, but let's init here)
admin = Admin(app, name='Photography Blog', url='/')

from app import routes, models
