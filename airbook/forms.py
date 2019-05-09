from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DateTimeField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from airbook.models import Customer, BookingAgent, AirlineStaff, Airline, Airport, Airplane, Flight
from sqlalchemy import or_
from datetime import datetime


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

    def validate_email(self, email):
        customer = Customer.query.filter_by(email=email.data).first()
        if customer:
            raise ValidationError('This email is taken.')


class CustomerLoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=50)])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Log in")


class CustomerEditForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=2, max=20)])
    address_building_number = StringField('Building Number',
                                          validators=[Length(max=20)])
    address_street = StringField('Building Number',
                                 validators=[Length(max=20)])
    address_city = StringField('City',
                               validators=[Length(max=20)])
    address_state = StringField('State',
                                validators=[Length(max=20)])
    phone_number = StringField('Phone Number',
                               validators=[Length(max=20)])
    passport_number = StringField('Passport Number',
                                  validators=[Length(max=20)])
    passport_expiration = DateField('Passport Expiration Date')
    passport_country = StringField('Passport Country',
                                   validators=[Length(max=30)])
    date_of_birth = DateField('Date of Birth')

    submit = SubmitField("Update Profile")


class BookingAgentRegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=50)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        booking_agent = BookingAgent.query.filter_by(
            email=email.data).first()
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

    def validate_username(self, username):
        airline_staff = AirlineStaff.query.filter_by(
            username=username.data).first()
        if airline_staff:
            raise ValidationError('This username is taken.')

    def validate_airline_name(self, airline_name):
        airline = Airline.query.filter_by(
            name=airline_name.data).first()
        if not airline:
            raise ValidationError('This airline does not exist.')


class AirlineStaffLoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=50)])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Log in")

# class TicketPurchaseForm(FlaskForm):


class SearchFlightForm(FlaskForm):
    source_place = StringField(
        "Source", validators=[DataRequired(), Length(max=20)])
    destination_place = StringField(
        "Destination", validators=[DataRequired(), Length(max=20)])
    departure_date = DateField("Departing")
    arrival_date = DateField("Arriving", validators=[Optional()])
    round_trip = BooleanField("Round Trip")
    submit = SubmitField("Search Flight")

    def validate_source_place(self, source_place):
        airport = Airport.query.filter(
            or_(Airport.name == source_place.data, Airport.city == source_place.data)).first()
        if not airport:
            raise ValidationError("Invalid source.")

    def validate_destination_place(self, destination_place):
        airport = Airport.query.filter(
            or_(Airport.name == destination_place.data, Airport.city == destination_place.data)).first()
        if not airport:
            raise ValidationError("Invalid destination.")

    def validate_departure_date(self, departure_date):
        if departure_date.data < datetime.utcnow().date():
            raise ValidationError("Departure date earlier than present.")

    def validate_arrival_date(self, arrival_date):
        if arrival_date.data and self.round_trip.data:
            if arrival_date.data < self.departure_date.data:
                raise ValidationError("Arrival before departure.")
            elif arrival_date.data < datetime.utcnow().date():
                raise ValidationError("Arrival date earlier than present.")


class PaymentForm(FlaskForm):
    payment_card_type = SelectField('Card Type', choices=[(
        'Debit', 'Debit Card'), ('Credit', 'Credit Card')])
    payment_card_number = StringField('Card Number',
                                      validators=[DataRequired(), Length(min=14, max=20)])
    payment_card_name = StringField('Card Holder Name',
                                    validators=[DataRequired(), Length(max=20)])
    payment_expiration_date = DateField("Expiration Date")

    submit = SubmitField("Purchase Ticket")

    def validate_payment_card_number(self, payment_card_number):
        if not payment_card_number.data.isnumeric():
            raise ValidationError("Card number must be a numeric combination.")


class AgentPaymentForm(FlaskForm):
    payment_card_type = SelectField('Card Type', choices=[(
        'Debit', 'Debit Card'), ('Credit', 'Credit Card')])
    payment_card_number = StringField('Card Number',
                                      validators=[DataRequired(), Length(min=14, max=20)])
    payment_card_name = StringField('Card Holder Name',
                                    validators=[DataRequired(), Length(max=20)])
    payment_expiration_date = DateField("Expiration Date")

    customer_email = StringField('Customer Email', validators=[
        DataRequired(), Length(max=50), Email()])

    submit = SubmitField("Purchase Ticket")

    def validate_customer_email(self, customer_email):
        customer = Customer.query.filter_by(email=customer_email.data).first()
        if not customer:
            raise ValidationError("This customer does not exist.")

    def validate_card_number(self, payment_card_number):
        if not payment_card_number.data.isnumeric():
            raise ValidationError("Card number must be a number.")


class FlightRegistrationForm(FlaskForm):
    airplane_id = SelectField('Airplane ID', choices=[],
                              validators=[DataRequired()])
    flight_number = StringField('Flight Number',
                                validators=[DataRequired(), Length(min=0, max=10)])
    base_price = FloatField("Base Price ($)", validators=[
                            DataRequired(), NumberRange(min=0, max=99999999)])
    departure_airport = StringField('Departure Airport',
                                    validators=[DataRequired(), Length(min=0, max=10)])
    arrival_airport = StringField('Arrival Airport',
                                  validators=[DataRequired(), Length(min=0, max=10)])
    departure_datetime = DateTimeField(
        "Departure Datetime", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    arrival_datetime = DateTimeField(
        "Arrival Datetime", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])

    submit = SubmitField("Create Flight")

    airline_name = ''

    def set_airline_name(self, name):
        self.airline_name = name

    def validate_flight_number(self, flight_number):
        airplane = Airplane.query.filter_by(
            id=self.airplane_id.data, airline_name=self.airline_name).first()
        airline_name = airplane.airline.name
        flight = Flight.query.filter_by(
            airline_name=airline_name, flight_number=flight_number.data).first()
        if flight:
            raise ValidationError("Flight number already taken.")

    def validate_departure_airport(self, departure_airport):
        airport = Airport.query.filter_by(name=departure_airport.data).first()
        if not airport:
            raise ValidationError("Invalid departure airport.")

    def validate_arrival_airport(self, arrival_airport):
        airport = Airport.query.filter_by(name=arrival_airport.data).first()
        if not airport:
            raise ValidationError("Invalid arrival airport.")

    def validate_departure_datetime(self, departure_datetime):
        if departure_datetime.data < datetime.utcnow():
            raise ValidationError('Departure datetime earlier than present.')

    def validate_arrival_datetime(self, arrival_datetime):
        if arrival_datetime.data < datetime.utcnow():
            raise ValidationError('Arrival datetime earlier than present.')
        elif arrival_datetime.data < self.departure_datetime.data:
            raise ValidationError("Arrival before departure.")


class FlightStatusEditForm(FlaskForm):
    status = SelectField('Flight Status', choices=[(
        'On-Time', 'On-Time'), ('Delayed', 'Delayed')])
    submit = SubmitField("Confirm Edit")


class AirplaneRegistrationForm(FlaskForm):
    airline_name = ''
    airplane_id = StringField('Airplane ID',
                              validators=[DataRequired(), Length(min=0, max=20)])
    num_of_seats = IntegerField("Number of Seats", validators=[
                                DataRequired(), NumberRange(min=1, max=9999)])
    submit = SubmitField("Register")

    def set_airline_name(self, name):
        self.airline_name = name

    def validate_airplane_id(self, airplane_id):
        airplane = Airplane.query.filter_by(
            id=airplane_id.data, airline_name=self.airline_name).first()
        if airplane:
            raise ValidationError('Airplane ID already taken.')


class AirportRegistrationForm(FlaskForm):
    name = StringField('Airport Name',
                       validators=[DataRequired(), Length(min=0, max=10)])
    city = StringField('City Name',
                       validators=[DataRequired(), Length(min=0, max=20)])
    country = StringField('Country Name',
                          validators=[DataRequired(), Length(min=0, max=30)])
    submit = SubmitField("Register")

    def validate_name(self, name):
        airport = Airport.query.get(name.data)
        if airport:
            raise ValidationError("Airport already exists.")


class DateRangeSelectionForm(FlaskForm):
    from_date = DateField('From', validators=[DataRequired()])
    to_date = DateField('To', validators=[DataRequired()])
    submit = SubmitField("Search")

    def validate_to_date(self, to_date):
        if to_date.data < self.from_date.data:
            raise ValidationError("To-date earlier than from-date")
        elif to_date.data > datetime.utcnow().date():
            raise ValidationError("To-date later than today.")
