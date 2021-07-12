from flask import Flask
from config import Config
import os

application = app = Flask(__name__)
app.config.from_object(Config)

if (not os.path.exists(app.config['CLIENT_FOLDER'])):
    os.mkdir(app.config['CLIENT_FOLDER'])

if (not os.path.exists(app.config['UPLOAD_FOLDER'])):
    os.mkdir(app.config['UPLOAD_FOLDER'])

if (not os.path.exists(app.config['DOWNLOAD_FOLDER'])):
    os.mkdir(app.config['DOWNLOAD_FOLDER'])

from app import routes
