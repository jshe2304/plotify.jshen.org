from re import L
import requests
from urllib.parse import urlencode, quote
import random

import os
import numpy as np
#import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
import base64
import json

from requests.api import get, head

from app import app



"""
Objectives:

Merge playlists
Reorganize
    Shuffle
    Alphabetical
    Reverse
    Song Name
    Song Artist
    Date Released
    Popularity

Filter By Characteristics

RYM ratings
Music Map


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
redirect_uri = "https://www.jshen.org/spotify/callback"
#redirect_uri = "http://localhost:5000/spotify/callback"
scopes = "ugc-image-upload user-read-recently-played user-top-read playlist-modify playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-follow-read user-library-modify user-library-read user-read-private"

albums = []
playlists = []

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

#URL Authentication

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

def valid_playlist(playlist_id):
    for playlist in playlists:
        if playlist['id'] == playlist_id:
            return True

    return False

def get_uid():
    return current_user()['uri']

#Useful JSON Functions

def unpage (json, params):
    if 'items' not in json and 'next' not in json:
        return None
    
    if 'next' == None:
        return json['items']

    items = json['items']

    next = json['next']

    while next != None:
        next_json = requests.get(next, params=params, headers=get_header()).json()
        items += next_json['items']
        next = next_json['next']

    return items

def chunk(n, lst):
    sections = []

    for i in range(0, len(lst), n):
        sections.append(lst[i:i + n])

    return sections


#Low Level API Functions

def playlist_tracks(playlist_id):

    params = {
        'fields': 'href, items(added_at, track(album.artists(name, uri), album.name, album.release_date, album.total_tracks, album.uri, duration_ms, name, popularity, track_number, uri)), limit, next, offset, previous, total'
    }

    paging_object = requests.get(BASE_URL + "playlists/" + playlist_id + "/tracks", params=params, headers=get_header()).json()

    playlist = unpage(paging_object, params)

    return playlist

def tracks_uris (tracks):

    uris = []

    for track in tracks:
        uris.append(track['track']['uri'])

    return uris

def tracks_ids (tracks):

    ids = []

    for track in tracks:
        ids.append(track['track']['uri'].split(":")[-1])

    return ids

def album_uris(album_id):
    params = {
        'limit': 50
    }

    paging_object = requests.get(BASE_URL + "albums/" + album_id + "/tracks", headers=get_header(), params=params).json()

    tracks = paging_object['items']

    if len(tracks) > 50:
        tracks = unpage(paging_object, None)

    uris = []

    for track in tracks:
        uris.append(track['uri'])

    return uris

def add_to_playlist(tracks, playlist_id):
    chunks = chunk(50, tracks)

    for chnk in chunks:
        uris = {'uris':chnk}
        requests.post(BASE_URL + "playlists/" + playlist_id + "/tracks", json=uris, headers=get_header())

def playlist_name (playlist_id):
    return requests.get(BASE_URL + "playlists/" + playlist_id, params={'fields': 'name'}, headers=get_header()).json()['name']

#User Library Functions

def get_albums():
    return albums

def get_playlists():
    return playlists

def request_albums():
    paging_object = requests.get(BASE_URL + "me/albums", headers=get_header()).json()

    #Album objects wrapped in SavedAlbum wrapper object
    #savedalbumobject['album']
    saved_albums = unpage(paging_object, None)

    albums = []

    for saved in saved_albums:
        albums.append(saved['album'])

    return albums

def request_playlists():
    #Playlist Name: list_json['name']
    #Playlist ID: list_json['id']

    paging_object = requests.get(BASE_URL + "me/playlists?limit=50",  headers=get_header()).json()

    playlists = unpage(paging_object, None)

    return playlists

def refresh_library():
    global albums
    global playlists

    albums = request_albums()
    playlists = request_playlists()

def public_playlists():
    public = []

    for playlist in playlists:
        if playlist['public'] == True:
            public.append(playlist)

    return public

def private_playlists():

    private = []

    for playlist in playlists:
        if playlist['public'] == False:
            private.append(playlist)

    return private

#High Level API Functions

def create_playlist (name, description):
    data = {
        'name': name,
        'description' : description,
    }

    uid = current_user()['id']

    response = requests.post(BASE_URL + "users/" + uid + "/playlists", json=data, headers=get_header()).json()

    return response

def shuffle_playlist(playlist_id):
    playlist = playlist_tracks(playlist_id)

    uris = tracks_uris(playlist)

    random.shuffle(uris)

    add_to_playlist(uris, create_playlist("Shuffled", None)['id'])

def combine_items(uris):

    tracks = []

    for uri in uris:
        uri_parts = str(uri).split(':')
        id = uri_parts[-1]
        if "playlist" in uri_parts:
            print (id)
            tracks += tracks_uris(playlist_tracks(id))
        elif "album" in uri_parts:
            print (id)
            tracks += album_uris(id)

    print (tracks)

    new_playlist = create_playlist("Combined - " + str(len(uris)) + " items", None)['id']

    add_to_playlist(tracks, new_playlist)

def reorganize_playlist(playlist_id, characteristic):
    playlist_json = requests.get(BASE_URL + "playlists/" + playlist_id, headers=get_header()).json()

    playlist_name = playlist_json['name']
    playlist_description = playlist_json['description']

    tracks = playlist_tracks(playlist_id)

    if characteristic == 'date':
        tracks.sort(key=release_date)
    elif characteristic == 'rdate':
        tracks.sort(reverse=True, key=release_date)

    add_to_playlist(playlist_tracks(tracks), create_playlist("Reorganized - " + playlist_name, playlist_description)['id'])
    
def sort_playlist(playlist_id, characteristics):
    None

#Playlist Basic Info
#Size

def playlist_size(playlist):
    #Takes playlist object, such as from get_playlist()
    return playlist['tracks']['items']['total']

#Analytics Functions

def popularity(track):
    return track['popularity']

def release_date(track):
    #Decimal Format

    track = track['track']

    release_str = track['album']['release_date'].split("-")

    release_num = None

    if len(release_str) == 0:
        return release_num
    elif len(release_str) == 1:
        release_num = int(release_str[0])
    elif len(release_str) == 2:
        days = int(release_str[1]) * 30.25
        release_num = int(release_str[0]) + days/365
    elif len(release_str) == 3:
        days = int(release_str[1]) * 30.25 + int(release_str[2])
        release_num = int(release_str[0]) + days/365
    
    return release_num

def genre(track):
    artist = requests.get(track['track']['artists'][0]['href'], headers=get_header()).json()
    
    if len(artist['genres']) != 0:
        return artist['genres'][0]
    else:
        return 'Unknown'

def common_genre(playlist):
    #Takes playlist object, return 5 most common genres

    None

def tracks_data (tracks):
    data = {
        'release dates': [],
        'popularities': []
    }

    for track in tracks:
        data['release dates'].append(release_date(track))
        data['popularities'].append(track['track']['popularity'])

    return data


def audio_features(tracks, target_field):
    ids = tracks_ids(tracks)

    chunks = chunk(100, ids)

    all_features = []

    for chnk in chunks:
        params = {
            'ids': ','.join(chnk)
        }

        chunk_features = requests.get(BASE_URL + 'audio-features', params=params, headers=get_header()).json()['audio_features']

        if target_field != None:
            all_features += [d[target_field] for d in chunk_features]

    return all_features

#Analytics

def dates_analysis(dates):
    #Density Plot, Mean, Median, Standard Deviation, 

    img = BytesIO()
    sns.set_style('dark')
    fig, ax1 = plt.subplots()
    ax1 = sns.kdeplot(x=dates, bw_adjust=.25, fill=True)
    ax1.set(ylabel=None)
    ax1.set(yticks=[])
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_b64 = base64.b64encode(img.getvalue()).decode('utf-8') #Base64 bytes to string

    dates = np.array(dates)

    mean = round(np.mean(dates))
    median = round(np.median(dates))
    stdev = round(np.std(dates), 2)

    #b64 is bytes so we convert to string

    return {'title': 'release date distribution', 'description': '', 'plot': plot_b64, 'figures': {'mean year': mean, 'median year': median, 'standard deviation': stdev}}

def valence_analysis(valences):

    description = 'valence essentially means happiness/sadness of a song'

    img = BytesIO()
    sns.set_style('dark')
    fig, ax1 = plt.subplots()
    ax1 = sns.kdeplot(x=valences, bw_adjust=.25, fill=True)
    ax1.set(ylabel=None)
    ax1.set(yticks=[])
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_b64 = base64.b64encode(img.getvalue()).decode('utf-8') #Base64 bytes to string

    valences = np.array(valences)

    mean = round(np.mean(valences), 3)
    median = round(np.median(valences), 3)
    stdev = round(np.std(valences), 3)

    #b64 is bytes so we convert to string

    return {'title': 'valence distribution', 'description': description, 'plot': plot_b64, 'figures': {'mean valence': mean, 'median valence': median, 'standard deviation': stdev}}

def date_valence_analysis(dates, valences):

    description = 'this plot is rather trivial, as, despite certain sterotypes, there will likely not be any relation between decades and the valence of their music. if you see such a relationship, congrats!'

    img = BytesIO()
    sns.set_style('dark')
    fig, ax1 = plt.subplots()
    ax1 = sns.scatterplot(x=dates, y=valences)
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_b64 = base64.b64encode(img.getvalue()).decode('utf-8') #Base64 bytes to string

    #b64 is bytes so we convert to string

    #dates = np.array(dates)
    #valences = np.array(valences)

    return {'title': 'release date versus valence', 'description': description, 'plot': plot_b64, 'figures': {}}

def popularity_analysis(popularities):

    img = BytesIO()
    sns.set_style('dark')
    fig, ax1 = plt.subplots()
    ax1 = sns.kdeplot(x=popularities, bw_adjust=.25, fill=True)
    ax1.set(ylabel=None)
    ax1.set(yticks=[])
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_b64 = base64.b64encode(img.getvalue()).decode('utf-8') #Base64 bytes to string

    valences = np.array(popularities)

    mean = round(np.mean(popularities))
    median = round(np.median(popularities))
    stdev = round(np.std(popularities))

    #b64 is bytes so we convert to string

    return {'title': 'popularity distribution', 'description': '', 'plot': plot_b64, 'figures': {'mean popularity': mean, 'median popularity': median, 'standard deviation': stdev}}

def top_songs ():
    for track in unpage(requests.get('https://api.spotify.com/v1/me/top/tracks', params={'time_range': 'long_term'}, headers=get_header()).json(), None):
        print (track['name'])

#GDPR Analytics

def history_analysis():
    data = []

    for filename in os.listdir(app.config['STREAMING_HISTORY_FOLDER']):
        data += json.load(open(app.config['STREAMING_HISTORY_FOLDER'] + '/' + filename))

    print(len(data))
