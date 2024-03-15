from flask_wtf import FlaskForm
from wtforms            import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(message="Please insert Password")])
    username = StringField('Username', validators=[DataRequired(message="Please insert Username")])