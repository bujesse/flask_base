from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, HiddenField, BooleanField


class MediaFilterForm(FlaskForm):
    site = SelectField('Site', coerce=int)
    media_type = SelectField('Media Type', coerce=int)
    tag = SelectField('Tag')
    topic = SelectField('Topic', coerce=int)
    weight = SelectField('Weight', coerce=int)
    source = SelectField('Source')
    channel = SelectField('Channel', coerce=int)
    search = StringField('Search (Searches title and description)')
    published_to_related_media = BooleanField('Related Media', default=False)
    published_to_video_page = BooleanField('Video Page', default=False)
    published_to_podcast_page = BooleanField('Podcast Page', default=False)
    submit = SubmitField('Submit')
