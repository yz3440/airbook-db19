from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class CustomerRegistrationForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=50)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")


class CustomerLoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired, Length(max=50)])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Log in")
