import os
import requests
from flask import Flask, render_template, flash, request, redirect, send_from_directory, abort, session
from flask.helpers import url_for

from app import app
from app.forms import GD_Form
from werkzeug.utils import secure_filename
from app.functions.generate_definitions import *

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title = 'Home')

@app.route('/version2')
def version2():
    return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

@app.route('/generate_definitions', methods=['POST', 'GET'])
def generatedefinitions():
    form = GD_Form()
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
    return render_template('generate_definitions.html', title = 'Generate Definitions For List of Terms', form=form)

#@app.route('/spotify-playlist-utilities', methods=['POST', 'GET'])
#def spotifyplaylistutilities_login():
    #CLIENT_ID = '4ed7461ce6fc46b9b5fc1cff6e08d2a5'

    #if request.method == "POST":
        
