from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    

class RegistrationForm(FlaskForm):
    businessname = StringField('Business Name', validators=[DataRequired()])
    businesstype = StringField('Business Type', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    number = StringField('Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message='Password should atleast be 8 characters long.')])
    # password2 = PasswordField(
    #     'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_number(self, number):
        user = User.query.filter_by(number=number.data).first()
        if user is not None:
            raise ValidationError('Please use a different number.')

    def validate_email(self, email):
        # included_chars = "@"
        # for char in self.email.data:
        #     if char in included_chars:
        #         pass
        #     else:
        #         raise ValidationError(
        #             f"Character @ is necessary in an email.")
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class PlatformForm(FlaskForm):
    file= FileField('File')
    days= IntegerField('Days', validators=[DataRequired()])
    submit = SubmitField('Get Forecast')

    