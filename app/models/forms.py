from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, MultipleFileField, SelectField
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired(), Length(min=6, max=32)])

class RegisterForm(Form):
    name = StringField("name", validators=[DataRequired()])
    lastname = StringField("lastname", validators=[DataRequired()])
    description = TextAreaField("description")
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired(), Length(min=6, max=32)])
    password_confirm = PasswordField("password_confirm", validators=[DataRequired(), Length(min=6, max=32)])

class UploadForm(Form):
    title = StringField("title", validators=[DataRequired()])
    category = SelectField("category", validators=[DataRequired()], 
                                        choices=[('caracterização territorial', 'Caracterização Territorial'), 
                                                ('demografia', 'Demografia'), 
                                                ('aspectos sociais', 'Aspectos Sociais'),
                                                ('infraestrutura', 'Infraestrutura'),
                                                ('aspectos economicos', 'Aspectos Econômicos')])
    fileshape = MultipleFileField("fileshape", validators=[FileRequired(), FileAllowed(['shp'], 'shapefiles')])