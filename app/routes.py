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
    return render_template('spotify_home.html', title='Spotify Utilities')

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

    user = current_user(authorized_token)

    print (user)

    return redirect(url_for('spotifyutilities', username=user['id']))

@app.route('/spotify-playlist-utilities/<username>', methods=['POST', 'GET'])
def spotifyutilities(username):
    return render_template('home.html')
