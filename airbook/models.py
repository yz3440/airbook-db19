from datetime import datetime
from airbook import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(id):
    id, role = id.split(',')

    if role == 'Customer':
        return Customer.query.get(id)
    elif role == 'Booking Agent':
        return BookingAgent.query.get(id)
    elif role == 'Airline Staff':
        return AirlineStaff.query.get(id)
    else:
        return None


class Airline(db.Model):
    name = db.Column(db.String(50), primary_key=True, nullable=False)
    airplanes = db.relationship('Airplane', backref='airline', lazy=True)
    airline_staffs = db.relationship(
        'AirlineStaff', backref='airline', lazy=True)

    def __repr__(self):
        return f"Airline('{self.name}')"


class Airport(db.Model):
    name = db.Column(db.String(10), primary_key=True, nullable=False)
    city = db.Column(db.String(20))
    country = db.Column(db.String(30))

    def __repr__(self):
        return f"Airport({self.name}, {self.city}, {self.country})"


class Airplane(db.Model):
    id = db.Column(db.String(20), primary_key=True, nullable=False)
    num_of_seats = db.Column(db.Numeric(4, 0), nullable=False)
    airline_name = db.Column(db.String(50), db.ForeignKey(
        'airline.name'), primary_key=True, nullable=False)
    flights = db.relationship('Flight', backref='airplane', lazy=True)


class Flight(db.Model):
    airline_name = db.Column(db.String(50), primary_key=True, nullable=False)
    airplane_id = db.Column(db.String(20), nullable=False)
    __table_args__ = (
        db.ForeignKeyConstraint(['airline_name', 'airplane_id'], [
            'airplane.airline_name', 'airplane.id']),
    )
    flight_number = db.Column(db.String(10), primary_key=True, nullable=False)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    departure_airport = db.Column(
        db.String(10), db.ForeignKey('airport.name'), nullable=False)
    departure_datetime = db.Column(db.DateTime, nullable=False)
    arrival_airport = db.Column(
        db.String(10), db.ForeignKey('airport.name'), nullable=False)
    arrival_datetime = db.Column(db.DateTime, nullable=False)
    tickets = db.relationship('Ticket', backref='flight', lazy=True)

    @property
    def seats_left(self):
        return self.airplane.num_of_seats - len(self.tickets)


class Customer(db.Model, UserMixin):
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), primary_key=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    address_building_number = db.Column(db.String(20))
    address_street = db.Column(db.String(20))
    address_city = db.Column(db.String(20))
    address_state = db.Column(db.String(20))
    phone_number = db.Column(db.String(20))
    passport_number = db.Column(db.String(20))
    passport_expiration = db.Column(db.Date)
    passport_country = db.Column(db.String(30))
    date_of_birth = db.Column(db.Date)

    tickets = db.relationship("Ticket", backref='customer', lazy=True)

    @property
    def id(self):
        return f'{self.email},Customer'

    @property
    def real_id(self):
        return self.email

    @property
    def role(self):
        return 'Customer'

    @property
    def display_name(self):
        return self.name

    @property
    def display_profile(self):
        return {
            'Address': f'{self.address_building_number}, {self.address_street}, {self.address_city}, {self.address_state}',
            'Phone Number': self.phone_number,
            'Passport Number': self.passport_number,
            'Passport Expiration': self.passport_expiration,
            'Passport Country': self.passport_country,
            "Date of Birth": self.date_of_birth}


class AirlineStaff(db.Model, UserMixin):
    username = db.Column(db.String(20), primary_key=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    airline_name = db.Column(db.String(50), db.ForeignKey(
        'airline.name'), nullable=False)
    phone_numbers = db.relationship(
        'AirlineStaffPhoneNumber', backref='owner', lazy=True)

    @property
    def id(self):
        return f'{self.username},Airline Staff'

    @property
    def real_id(self):
        return self.username

    @property
    def role(self):
        return 'Airline Staff'

    @property
    def display_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def display_profile(self):
        return {
            'Airline Name': self.airline_name,
            'Date of Birth': self.date_of_birth}


class AirlineStaffPhoneNumber(db.Model):
    username = db.Column(db.String(20), db.ForeignKey(
        'airline_staff.username'), primary_key=True, nullable=False)
    phone_number = db.Column(db.String(20), primary_key=True, nullable=False)


class BookingAgent(db.Model, UserMixin):
    email = db.Column(db.String(50), primary_key=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    booking_agent_id = db.Column(db.String(10), unique=True, nullable=False)
    tickets = db.relationship(
        'Ticket', backref='seller', lazy=True)

    @property
    def id(self):
        return f'{self.email},Booking Agent'

    @property
    def real_id(self):
        return self.email

    @property
    def role(self):
        return 'Booking Agent'

    @property
    def display_name(self):
        return self.email

    @property
    def display_profile(self):
        return {
            'Booking Agent ID': self.booking_agent_id}


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    airline_name = db.Column(db.String(50), nullable=False)
    flight_number = db.Column(db.String(10), nullable=False)
    __table_args__ = (
        db.ForeignKeyConstraint(['airline_name', 'flight_number'], [
            'flight.airline_name', 'flight.flight_number']),
    )
    sold_price = db.Column(db.Numeric(10, 2), nullable=False)
    customer_email = db.Column(db.String(50), db.ForeignKey(
        'customer.email'), nullable=False)
    payment_card_type = db.Column(db.String(10), nullable=False)
    payment_card_number = db.Column(db.String(20), nullable=False)
    payment_card_name = db.Column(db.String(20), nullable=False)
    payment_expiration_date = db.Column(db.Date, nullable=False)
    booking_agent_id = db.Column(db.String(10), db.ForeignKey(
        'booking_agent.booking_agent_id'), nullable=True)
    purchase_datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def commision(self):
        return self.sold_price / 10 if self.booking_agent_id else None
