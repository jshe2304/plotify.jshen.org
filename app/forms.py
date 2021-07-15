from flask_wtf import FlaskForm
from wtforms import FileField, RadioField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class DefGeneratorForm(FlaskForm):
    def_source = RadioField('Definition Source', choices=['Dictionary', 'Wikipedia'], validators=[DataRequired()])
    omit_term = BooleanField("Omit Term From Definition")
    file = FileField('Submit File', validators=[DataRequired()])
    separator = RadioField('Separator', choices=['New Line', 'Comma (,)', 'Period (.)', 'Semicolon (;)', 'Colon (:)', 'Slash (/)', 'Pipe (|)'], validators=[DataRequired()])
    submit = SubmitField('Process File')

#class spu_login_form(FlaskForm):
    #None
    