from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from airbook.models import Customer, BookingAgent, AirlineStaff, Airline


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

    def validate_email(self, field):
        customer = Customer.query.filter_by(email=self.email.data).first()
        if customer:
            raise ValidationError('This email is taken.')


class CustomerLoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=50)])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Log in")


class BookingAgentRegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=50)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")

    def validate_email(self, field):
        booking_agent = BookingAgent.query.filter_by(
            email=self.email.data).first()
        if booking_agent:
            raise ValidationError('This email is taken.')


class BookingAgentLoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=50)])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Log in")


class AirlineStaffRegistrationForm(FlaskForm):
    first_name = StringField('First Name',
                             validators=[DataRequired(), Length(max=20)])
    last_name = StringField('Last Name',
                            validators=[DataRequired(), Length(max=20)])
    date_of_birth = DateField("Date of Birth")
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=50)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password')])
    airline_name = StringField('Airline Name',
                               validators=[DataRequired(), Length(max=50)])

    submit = SubmitField("Sign Up")

    def validate_username(self, field):
        airline_staff = AirlineStaff.query.filter_by(
            username=self.username.data).first()
        if airline_staff:
            raise ValidationError('This username is taken.')

    def validate_airline_name(self, field):
        airline = Airline.query.filter_by(
            name=self.airline_name.data).first()
        if not airline:
            raise ValidationError('This airline does not exist.')


class AirlineStaffLoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=50)])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Log in")


class SearchFlightForm(FlaskForm):
    source_place = StringField(
        "Source", validators=[DataRequired(), Length(max=20)])
    destination_place = StringField(
        "Destination", validators=[DataRequired(), Length(max=20)])
    departure_date = DateField("Departing")
    arrival_date = DateField("Arriving")
    round_trip = BooleanField("Round Trip")
    submit = SubmitField("Search Flight")
