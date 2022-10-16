from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired(), Length(1, 256)])
