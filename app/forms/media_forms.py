from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, BooleanField, SelectMultipleField, FileField
from wtforms.validators import ValidationError, Optional, InputRequired
from wtforms.widgets import HTMLString, TextInput

from app.models.blockbuster import Media, MediaType, Channel
from app.helpers import get_source_select

from app.helpers import sanitize_slug

from quill_libs.elasticsearch.meta import (
    TagService,
    TagQueryBuilder
)


class DropzoneWidget(TextInput):
    def __init__(self, dropzone_classes=None, *args, **kwargs):
        self.dropzone_classes = dropzone_classes or ''
        super(DropzoneWidget, self).__init__(*args, **kwargs)

    def __call__(self, field, **kwargs):
        html = super(DropzoneWidget, self).__call__(field, **kwargs)
        params = {'id': (field.id + '-dz'), 'class': 'dropzone ' + self.dropzone_classes}
        return html + HTMLString('<div {}><div class="dz-message" data-dz-message><span>Drag image here or click to upload</span></div></div>'.format(self.html_params(**params)))


class TagValidator(object):
    def __call__(self, form, field):
        is_weight = form.weight.data != None
        tag_slugs = [t.strip() for t in field.data.split(',')]
        if tag_slugs == ['']:
            form.tag_placeholder = []
            return
        if tag_slugs and not is_weight:
            # PS-637 - Putting check test preserves tag list as typed
            form.errors.update({'weight': ['Must have a weight if saving tags.']})
            return
        service = TagService(config=current_app.config.get('QUILL_ELASTICSEARCH'))
        res = service.get(query=TagQueryBuilder(tag_type='cbcontent', slug=[sanitize_slug(s) for s in tag_slugs]))
        form.tag_placeholder = list(res)
        if len(res) != len(tag_slugs):
            found_slugs = [t['slug'] for t in res]
            raise ValidationError('Unable to find tags in Quill: {}'.format(', '.join(t for t in tag_slugs if t not in found_slugs)))


class WeightValidator(object):
    def __call__(self, form, field):
        is_weight = field.data is not None
        is_tag = form.tag.data != ''
        if field.data == 0:
            return
        if is_weight and field.data not in list(range(1, 11)):
            raise ValidationError('Please enter a number between 1 and 10')
        elif (is_weight and is_tag) or (not is_weight and not is_tag):
            return
        elif not is_tag and is_weight:
            form.errors.update({'tag': ['Must have at least 1 tag in order to save weight.']})


class MediaTypeValidator(object):
    def __call__(self, form, field):
        media_type = MediaType.query.filter_by(id=field.data).first()
        if media_type.name == 'podcast':
            if form.channel.data == 0:
                form.errors.update({'channel': ['Required for Media Type: Podcast']})
            if not form.episode_number.data:
                form.errors.update({'episode_number': ['Required for Media Type: Podcast']})


class ChannelValidator(object):
    def __call__(self, form, field):
        channel = Channel.query.filter_by(id=field.data).first()
        media_type = MediaType.query.filter_by(id=form.media_type_id.data).first()
        if channel and channel.media_type != media_type.id:
            form.errors.update({'channel': ['Channel must be for selected Media Type: {}'.format(media_type.name)]})


class PublishedToRelatedMediaValidator(object):
    def __call__(self, form, field):
        if field.data:
            if not form.topic.data:
                form.errors.update({'topic': ['Must select at least 1 topic to Publish to Related Media']})


class PublishedToVideoPageValidator(object):
    def __call__(self, form, field):
        if field.data:
            media_type = MediaType.query.filter_by(id=form.media_type_id.data).first()
            if media_type.name != 'video':
                form.errors.update({'media_type_id': ['Must be "Video" to publish to Video page']})


class PublishedToPodcastPageValidator(object):
    def __call__(self, form, field):
        if field.data:
            media_type = MediaType.query.filter_by(id=form.media_type_id.data).first()
            if media_type.name != 'podcast':
                form.errors.update({'media_type_id': ['Must be "Podcast" to publish to Podcast page']})

class CBDBValidator(object):
    def __call__(self, form, field):
        if field.data and not form.cover_image_wide.data:
            raise ValidationError('Must have at least a cover image to associate to CBDB.')


class MediaForm(FlaskForm):
    title = StringField('Title*', validators=[InputRequired()])
    slug = StringField('Slug', validators=[Optional()], description='Created automatically if empty')
    site = SelectField('Site*', coerce=int)

    media_type_id = SelectField('Media Type*', coerce=int, validators=[MediaTypeValidator()])
    channel = SelectField('Media Channel', coerce=int, validators=[Optional(), ChannelValidator()])

    cover_image = StringField('Cover Image - Square', widget=DropzoneWidget(), validators=[Optional()])
    cover_image_wide = StringField('Cover Image - Wide', widget=DropzoneWidget(dropzone_classes='dropzone-wide'), validators=[Optional()])

    description = StringField('Description', validators=[Optional()])
    source = SelectField('Media Source*', choices=get_source_select(Media, required=True), validators=[Optional()])
    foreign_media_id = StringField('Media ID*', validators=[InputRequired()])
    episode_number = IntegerField('Episode Number', validators=[Optional()])
    weight = IntegerField('Weight [1-10]', validators=[WeightValidator(), Optional()])
    topic = SelectMultipleField('Topics')
    tag = StringField('Tags', validators=[TagValidator()], description='Must exist in Quill.')

    cbdb_title = StringField('CBDB Title', validators=[Optional(), CBDBValidator()])
    cbdb_genre = StringField('CBDB Genre', validators=[Optional(), CBDBValidator()])
    cbdb_franchise = StringField('CBDB Franchise', validators=[Optional(), CBDBValidator()])
    cbdb_series = StringField('CBDB Series', validators=[Optional(), CBDBValidator()])
    cbdb_studio = StringField('CBDB Studio', validators=[Optional(), CBDBValidator()])
    cbdb_person = StringField('CBDB Person', validators=[Optional(), CBDBValidator()])

    featured_zone = SelectMultipleField('Featured Zones', coerce=int)

    published_to_related_media = BooleanField('<b>Publish to Related Media</b>', default=False, validators=[PublishedToRelatedMediaValidator()])
    published_to_video_page = BooleanField('<b>Publish to Video Page</b>', default=False, validators=[PublishedToVideoPageValidator()])
    published_to_podcast_page = BooleanField('<b>Publish to Podcast Page</b>', default=False, validators=[PublishedToPodcastPageValidator()])

    submit = SubmitField('Submit')

    # If we manipulate the tags during validation but another field fails,
    # it interferes with the tag display on the followup form.
    # Use this placeholder so we only swap the tags value on a successful validation.
    # TODO: May also look into using a custom field type with an overridden post_validate.
    tag_placeholder = None

    def validate(self):
        if not super().validate():
            return False

        is_valid = True
        if (self.published_to_podcast_page.data or self.published_to_video_page.data) and not self.cover_image.data:
            self.cover_image.errors.append('You must select a cover image when publishing to video or podcast pages')
            is_valid = False

        return is_valid

    def validate_on_submit(self):
        if self.is_submitted():
            is_valid = self.validate()
            if self.errors:
                is_valid = False
                for field, error in self.errors.items():
                    getattr(self, field).errors = error
            else:
                self.tag.data = self.tag_placeholder
            return is_valid
        return False
