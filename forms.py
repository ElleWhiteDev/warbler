import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Optional
from flask_wtf.file import FileField, FileAllowed


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


def validate_image_url(form, field):
    """Custom validator to check if a URL ends with .jpg, .png, or .svg"""

    if field.data:
        if not re.search(r'(.jpg|.png|.svg)$', field.data):
            raise ValidationError("Invalid URL! Please provide a URL that ends with .jpg, .png, or .svg")


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6, max=20)])
    profile_img = FileField('(Optional) Profile Image Upload', validators=[FileAllowed(['jpg', 'png'])])
    profile_img_url = StringField('Or Provide an Image URL', validators=[Optional()])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6, max=20)])


class EditUserForm(FlaskForm):
    """Edit user profile form"""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    profile_img = FileField('(Optional) Profile Image Upload', validators=[FileAllowed(['jpg', 'png'])])
    profile_img_url = StringField('Or Provide A Profile Image URL', validators=[Optional(), validate_image_url])
    header_img = FileField('(Optional) Banner Picture', validators=[FileAllowed(['jpg', 'png'])])
    header_img_url = StringField('Or Provide A Banner Image URL', validators=[Optional(), validate_image_url])
    bio = TextAreaField('(Optional) Bio', validators=[Optional(), Length(max=200)])
    password = PasswordField('Current Password', validators=[DataRequired()])
