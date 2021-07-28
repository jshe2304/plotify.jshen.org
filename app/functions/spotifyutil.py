from re import L
import requests
from urllib.parse import urlencode, quote
import random

from app import app

"""
Objectives:

Merge playlists
Shuffle Playlist

"""

#Client Credentials
CLIENT_ID = app.config['SPOTIFY_CLIENT_ID']
CLIENT_SECRET = app.config['SPOTIFY_CLIENT_SECRET']

#URLs
BASE_URL = 'https://api.spotify.com/v1/'
AUTH_URL = 'https://accounts.spotify.com/api/token'
OAUTH_URL = 'https://accounts.spotify.com/authorize'

#Base Token and Header
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']

#OAuth Query Parameters
response_type = "code"
redirect_uri = "http://localhost:5000/spotify-playlist-utilities/callback"
scopes = "ugc-image-upload user-read-recently-played user-top-read user-read-playback-position user-read-currently-playing streaming playlist-modify playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-follow-read user-library-modify user-library-read user-read-email user-read-private"


#OAuth Functions

def oauth_url():
    params = {
        'client_id' : CLIENT_ID,
        'response_type' : response_type,
        'redirect_uri' : redirect_uri,
    }

    query = urlencode(params) + "&scope=" + quote(scopes)

    return OAUTH_URL + "?" + query

def request_authorized_token(code):
    params = {
        'grant_type' : "authorization_code",
        'code' : code,
        'redirect_uri' : redirect_uri,
        'client_id' : CLIENT_ID,
        'client_secret' : CLIENT_SECRET,
    }

    response = requests.post(AUTH_URL, params).json()

    return response['access_token']

def set_token(new_token):
    global access_token
    access_token = new_token

def get_header():
    return {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }


def current_user():
    user = requests.get(BASE_URL + "me", headers=get_header()).json()

    return user

def authenticated_user(username):
    user = current_user()
    #print(user['id'])
    #print(username)
    if user['id'] == username:
        return True
    
    return False

def get_uid():
    return current_user()['uri']

def unpage (json):
    if 'items' not in json and 'next' not in json:
        return None
    
    if 'next' == None:
        return json['items']

    items = json['items']

    next = json['next']

    while next != None:
        next_json = requests.get(next, headers=get_header()).json()
        items += next_json['items']
        next = next_json['next']

    return items

def list_of_playlists():
    #Playlist Name: list_json['name']
    #Playlist ID: list_json['id']

    paging_object = requests.get(BASE_URL + "me/playlists?limit=50", headers=get_header()).json()

    playlists = unpage(paging_object)

    return playlists

def valid_playlist(playlist_id):
    playlists = list_of_playlists()

    for playlist in playlists:
        if playlist['id'] == playlist_id:
            return True

    return False

def valid_url(username, playlist):
    if not authenticated_user(username):
        return False
    if not valid_playlist(playlist):
        False
    return None
            
def list_of_tracks(playlist_id):
    #Test playlist: 6Sko93pvXQ4ByuEJXHAcKT
    #Track Info: track_json['track']
    #Track Name: track_json['track']['name']
    #Track id: track_json['track']['id']

    songs = []

    if playlist_id == "" or len(playlist_id) != 22:
        return songs

    paging_object = requests.get(BASE_URL + "playlists/" + playlist_id + "/tracks", headers=get_header()).json()
    
    playlist = unpage(paging_object)

    uris = []

    for track in playlist:
        uris.append(track['track']['uri'])

    return uris

def create_playlist (name, description):
    data = {
        'name': name,
        'description' : description,
    }

    uid = current_user()['id']

    print (uid)

    response = requests.post(BASE_URL + "users/" + uid + "/playlists", json=data, headers=get_header()).json()

    return response

def chunk(n, lst):
    sections = []

    for i in range(0, len(lst), n):
        sections.append(lst[i:i + n])

    return sections

def shuffle_playlist(playlist_id):
    playlist_json = requests.get(BASE_URL + "playlists/" + playlist_id, headers=get_header()).json()

    playlist_name = playlist_json['name']
    playlist_description = playlist_json['description']

    tracks = list_of_tracks(playlist_id)

    new_playlist = create_playlist("Shuffled - " + playlist_name, playlist_description)

    random.shuffle(tracks)

    chunks = chunk(50, tracks)

    for chnk in chunks:
        uris = {'uris':chnk}
        requests.post(BASE_URL + "playlists/" + new_playlist['id'] + "/tracks", json=uris, headers=get_header())



