from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length


class GistForm(FlaskForm):
    """ Generates form to create GitHub Gists """

    filename = StringField('Filename', validators=[
                           DataRequired(), Length(min=3, max=100)])

    description = StringField('Description')

    gist_content = TextAreaField('Gist Content', validators=[
                                 DataRequired(), Length(min=3, max=1000)])

    is_public_gist = BooleanField('Public Gist', default=False)

    submit = SubmitField('Publish Gist')


class LoginForm(FlaskForm):
    """ Form for starting OAuth2 flow """

    submit = SubmitField('Login with GitHub')
