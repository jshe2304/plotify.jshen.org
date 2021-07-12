import os
from flask import Flask, render_template, flash, request, redirect, send_from_directory, abort, session
from flask.helpers import url_for

from app import app
from app.forms import GenerateDefsForm
from werkzeug.utils import secure_filename
from app.static.functions import *

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title = 'Home')

@app.route('/generate_definitions', methods=['post', 'get'])
def generatedefinitions():
    form = GenerateDefsForm()
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
