from flask_wtf import FlaskForm
from wtforms import FileField, MultipleFileField, RadioField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class DefGeneratorForm(FlaskForm):
    def_source = RadioField('definition Source', choices=['dictionary', 'wikipedia'], validators=[DataRequired()])
    omit_term = BooleanField("omit term from definition")
    file = FileField('submit file', validators=[DataRequired()])
    separator = RadioField('separator', choices=['new Line', 'comma (,)', 'period (.)', 'semicolon (;)', 'colon (:)', 'slash (/)', 'pipe (|)'], validators=[DataRequired()])
    submit = SubmitField('process file')

class SpotifyGdprForm(FlaskForm):
    file = MultipleFileField('input json files', validators=[DataRequired()])
    submit = SubmitField('submit json files')