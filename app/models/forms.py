from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField
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
    
