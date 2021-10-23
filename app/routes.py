import os
from random import choices
from flask.helpers import url_for
from flask import render_template, flash, request, redirect, send_from_directory

from app import app
from app.forms import DefGeneratorForm, SpotifyCombineForm
from werkzeug.utils import secure_filename
from app.functions.defgenerator import *
from app.functions.spotifyutil import *
from wtforms import BooleanField

#Home Page

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title = 'Home')


#Definition Generator

@app.route('/definition_generator', methods=['POST', 'GET'])
def generatedefinitions():
    form = DefGeneratorForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            def_source = form.def_source.data
            omit_term = form.omit_term.data
            separator = form.separator.data
            file = request.files['file']
            filename = secure_filename(file.filename)
            if filename[-4:].split(".")[-1] in app.config['ALLOWED_EXTENSIONS']:
                
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                generate_definitions(def_source, omit_term, separator, filename)
            
                return send_from_directory(app.config["DOWNLOAD_FOLDER"], path = "definitions.pdf", as_attachment=True)
            else:
                flash ("File Extension Not Supported")
        else:
            flash("Field Required")
    return render_template('def_generator.html', title = 'Generate Definitions For List of Terms', form=form)


#Spotify Playlist Utilities

@app.route('/spotify', methods=['POST', 'GET'])
def spotifyutilitieshome():
    return render_template('/spotify/spotify_home.html', title='Spotify Utilities')


@app.route('/spotify/login')
def spotifyutilitieslogin():
    print ('checkpoint 1')
    query = oauth_url()
    return redirect(query)

@app.route('/spotify/callback')
def spotifyutilitiescallback():

    response = request.args

    if len(response) == 0 or 'error' in response:
        return redirect("/spotify")

    code = response['code']

    authorized_token = request_authorized_token(code)
    set_token(authorized_token)

    user = current_user()

    return redirect('/spotify/' + user['id'])


@app.route('/spotify/<username>', methods=['POST', 'GET'])
def spotify(username):
    if not authenticated_user(username):
        return redirect('/spotify')

    refresh_library()

    playlists = get_playlists()
    albums = get_albums()

    public = public_playlists()
    private = private_playlists()

    return render_template('/spotify/spotify.html', playlists=playlists, public=public, private=private, albums=albums, username=username)

@app.route('/spotify/<username>/combine', methods=['POST', 'GET'])
def spotifycombine(username):
    if not authenticated_user(username):
        return redirect('/spotify')

    playlists = get_playlists()
    albums = get_albums()

    class SpotifyCombineInstance(SpotifyCombineForm):
        pass

    for playlist in playlists:
        setattr(SpotifyCombineInstance, playlist['uri'], BooleanField(playlist['name']))

    for album in albums:
        setattr(SpotifyCombineInstance, album['uri'], BooleanField(album['name']))

    form = SpotifyCombineInstance(request.form)

    if request.method == "POST":
        response = request.form

        items = response.to_dict(False)

        uris = []
        for item in items:
            if "spotify" in item:
                uris.append(item)

        combine_items(uris)

        refresh_library()

        return redirect('/spotify/' + username)

    return render_template('/spotify/spotify_combine.html', form=form, playlists=playlists, albums=albums)

@app.route('/spotify/<username>/<playlist_id>', methods = ['POST', 'GET'])
def spotifyplaylist(username, playlist_id):
    if not authenticated_user(username):
        return redirect('/spotify')
    if not valid_playlist(playlist_id):
        return redirect('/spotify/' + username)

    tracks = playlist_tracks(playlist_id)

    data = tracks_data(tracks)
    valences = audio_features(tracks, 'valence')


    plots = [dates_analysis(data['release dates']), valence_analysis(valences), date_valence_analysis(data['release dates'], valences), popularity_analysis(data['popularities'])]

    return render_template('/spotify/spotify_playlist.html', username=username, playlist_name=playlist_name(playlist_id), id = playlist_id, plots=plots)

@app.route('/spotify/<username>/<playlist_id>/utilities', methods = ['POST', 'GET'])
def spotifyutilities(username, playlist_id):
    if not authenticated_user(username):
        return redirect('/spotify')
    if not valid_playlist(playlist_id):
        return redirect('/spotify/' + username)

    return render_template('/spotify/spotify_playlist_utilities.html', username=username, id=playlist_id)

@app.route('/spotify/<username>/<playlist_id>/shuffle', methods = ['POST', 'GET'])
def spotifyshuffle(username, playlist_id):
    if not authenticated_user(username):
        return redirect('/spotify')
    if not valid_playlist(playlist_id):
        return redirect('/spotify/' + username)

    shuffle_playlist(playlist_id)

    refresh_library()

    return redirect('/spotify/' + username + "/" + playlist_id + "/utilities")

@app.route('/spotify/<username>/<playlist_id>/reorganize/<characteristic>', methods = ['POST', 'GET'])
def spotifyreorganize(username, playlist_id, characteristic):
    if not authenticated_user(username):
        return redirect('/spotify')
    if not valid_playlist(playlist_id):
        return redirect('/spotify/' + username)

    if characteristic == 'date':
        reorganize_playlist(playlist_id, 'date')
    elif characteristic == 'rdate':
        reorganize_playlist(playlist_id, 'rdate')

    return redirect('/spotify/' + username + "/" + playlist_id)
