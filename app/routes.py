import os
from flask.helpers import url_for
from flask import render_template, flash, request, redirect, send_from_directory

from app import app
from app.forms import DefGeneratorForm
from werkzeug.utils import secure_filename
from app.functions.defgenerator import *
from app.functions.spotifyutil import *

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title = 'Home')

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

@app.route('/spotify-playlist-utilities', methods=['POST', 'GET'])
def spotifyutilitieshome():
    return render_template('/spotify/spotify_home.html', title='Spotify Utilities')

@app.route('/spotify-playlist-utilities/login')
def spotifyutilitieslogin():
    query = oauth_url()
    return redirect(query)

@app.route('/spotify-playlist-utilities/callback')
def spotifyutilitiescallback():

    response = request.args

    if len(response) == 0 or 'error' in response:
        return redirect("/spotify-playlist-utilities")

    code = response['code']

    authorized_token = request_authorized_token(code)
    set_token(authorized_token)

    user = current_user()

    return redirect('/spotify-playlist-utilities/' + user['id'])

@app.route('/spotify-playlist-utilities/<username>', methods=['POST', 'GET'])
def spotifyutilities(username):
    if not authenticated_user(username):
        return redirect('/spotify-playlist-utilities')

    playlists = list_of_playlists()
    return render_template('/spotify/spotify_utilities.html', playlists=playlists, username=username)

@app.route('/spotify-playlist-utilities/<username>/<playlist_id>', methods = ['POST', 'GET'])
def spotifyplaylist(username, playlist_id):
    if not authenticated_user(username):
        return redirect('/spotify-playlist-utilities')
    if not valid_playlist(playlist_id):
        return redirect('/spotify-playlist-utilities/' + username)

    return render_template('/spotify/spotify_playlist.html', username=username, playlist_id=playlist_id)

@app.route('/spotify-playlist-utilities/<username>/<playlist_id>/shuffle', methods = ['POST', 'GET'])
def spotifyshuffle(username, playlist_id):
    if not authenticated_user(username):
        return redirect('/spotify-playlist-utilities')
    if not valid_playlist(playlist_id):
        return redirect('/spotify-playlist-utilities/' + username)

    shuffle_playlist(playlist_id)

    return redirect('/spotify-playlist-utilities/' + username + "/" + playlist_id)