import re
import requests
import math
from urllib.parse import urlencode

from requests.api import head
from werkzeug.utils import redirect

"""
Objectives:

Merge playlists
Shuffle Playlist

"""

CLIENT_ID = '4ed7461ce6fc46b9b5fc1cff6e08d2a5'
CLIENT_SECRET = '97abd660e7a94dc587930582a691b22b'

BASE_URL = 'https://api.spotify.com/v1/'
AUTH_URL = 'https://accounts.spotify.com/api/token'
OAUTH_URL = 'https://accounts.spotify.com/authorize?'

response_type = "code"
redirect_uri = "http://localhost:5000/spotify-playlist-utilities/callback"
scopes = "user-library-read user-library-modify playlist-read-private playlist-modify-private playlist-modify-public user-library-read"

auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']



def oauth_url():
    params = {
        'client_id' : CLIENT_ID,
        'response_type' : response_type,
        'redirect_uri' : redirect_uri,
        'scopes' : scopes,
    }

    query = urlencode(params)

    return OAUTH_URL + query

def request_authorized_token(code):
    params = {
        'grant_type' : "authorization_code",
        'code' : code,
        'redirect_uri' : redirect_uri,
        'client_id' : CLIENT_ID,
        'client_secret' : CLIENT_SECRET,
    }

    response = requests.post(AUTH_URL, params).json()

    #print (response)

    return response['access_token']

def set_token(new_token):
    global access_token
    access_token = new_token

def get_header():
    return {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

def current_user(token):

    user = requests.get(BASE_URL + "me", headers=get_header()).json()

    return user

def list_of_tracks(playlist_id, output):
    songs = []

    if playlist_id == "" and len(playlist_id) != 22:
        return songs

    playlist = requests.get(BASE_URL + "playlists/" + playlist_id + "/tracks", headers=get_header()).json()
    
    total = playlist['total']
    
    for i in range(int(math.ceil(total/100))):
        items = playlist['items']
        for song in items:
            if output == "name":
                songs.append(song['track']['name'])
            elif output == "uri":
                songs.append(song['track']['uri'])

        if playlist['next'] != None:
            playlist = requests.get(playlist['next'], headers=get_header()).json()
    
    return songs

#songs = list_of_tracks("1HDBhTV7Bc0lx94M630bfm", "uri")
#print (songs)
#print (len(songs))
#print (len("1HDBhTV7Bc0lx94M630bfm"))

def create_playlist (user_id, name, description):
    data = {
        name: name,
        description: description
    }

    response = requests.post(BASE_URL + "users/" + user_id + "/playlists", data=data, headers=get_header())

    return response.content


