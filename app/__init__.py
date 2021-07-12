from flask import Flask
from config import Config
import os

application = app = Flask(__name__)
app.config.from_object(Config)

#if (os.path.exists())
#os.mkdir(app.config['UPLOAD_FOLDER'])

from app import routes
