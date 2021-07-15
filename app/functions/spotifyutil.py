import requests
import math

from requests.api import head

"""
Objectives:

Merge playlists
Shuffle Playlist

"""

CLIENT_ID = '4ed7461ce6fc46b9b5fc1cff6e08d2a5'
CLIENT_SECRET = '97abd660e7a94dc587930582a691b22b'

AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'

def list_of_tracks(playlist_id, output):
    songs = []

    if playlist_id == "" and len(playlist_id) != 22:
        return songs

    playlist = requests.get(BASE_URL + "playlists/" + playlist_id + "/tracks", headers=headers).json()
    
    total = playlist['total']
    
    for i in range(int(math.ceil(total/100))):
        items = playlist['items']
        for song in items:
            if output == "name":
                songs.append(song['track']['name'])
            elif output == "uri":
                songs.append(song['track']['uri'])

        if playlist['next'] != None:
            playlist = requests.get(playlist['next'], headers=headers).json()
    
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

    response = requests.post(BASE_URL + "users/" + user_id + "/playlists", data=data, headers=headers)

    return response.content

print (create_playlist("fro8ozz", "test name", "test description"))


