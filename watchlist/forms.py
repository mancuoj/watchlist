from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, PasswordField
from wtforms.validators import DataRequired, Length


class MovieForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 60)])
    year = StringField("Year", validators=[DataRequired(), Length(4, 4)])


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(1, 128)])


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(1, 128)])
    password_confirmation = PasswordField(
        "Confirm Password", validators=[DataRequired(), Length(1, 128)]
    )


class SettingsForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 20)])


class CommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired(), Length(1, 256)])
