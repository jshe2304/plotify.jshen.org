import os
from os.path import join, dirname, realpath

class Config (object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "6^0)1!0)5%1!4$1!1!9("

    abspath = dirname(realpath(__file__))
    CLIENT_FOLDER = join(abspath, "app/client")
    UPLOAD_FOLDER = join(CLIENT_FOLDER, "upload")
    DOWNLOAD_FOLDER = join(CLIENT_FOLDER, "download")

    DEFINITIONS_ALLOWED_EXTENSIONS = ['docx', 'pdf', 'txt']
    SPOTIFY_GDPR_ALLOWED_EXTENSIONS = ['json']
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    SPOTIFY_CLIENT_ID = '4ed7461ce6fc46b9b5fc1cff6e08d2a5'
    SPOTIFY_CLIENT_SECRET = '97abd660e7a94dc587930582a691b22b'


    #UPLOAD_FOLDER = "client/upload"
    #DOWNLOAD_FOLDER = "client/download"