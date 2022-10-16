from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(1, 128)])


class CommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired(), Length(1, 256)])
