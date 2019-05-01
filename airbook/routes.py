from flask import render_template, flash, redirect, url_for, request
from airbook import app, db, bcrypt
from airbook.forms import CustomerRegistrationForm, CustomerLoginForm, BookingAgentRegistrationForm, BookingAgentLoginForm, AirlineStaffRegistrationForm, AirlineStaffLoginForm, SearchFlightForm
from airbook.models import Airline, Airport, Airplane, Flight, Customer, AirlineStaff, AirlineStaffPhoneNumber, BookingAgent, Ticket
from flask_login import login_user, logout_user, current_user, login_required
from airbook.utils import id_generator


@app.route("/")
@app.route("/search_flight", methods=['GET', 'POST'])
def home():
    print(current_user)

    flights = Flight.query.all()
    form = SearchFlightForm()
    if form.validate_on_submit():
        print(form.arrival_date.data)
        print(type(form.departure_date.data))
        print(form.arrival_date.data > form.departure_date.data)

    return render_template('search_flight.html', title="Search Result", flights=flights, form=form)


@app.route("/register", methods=['GET', 'POST'])
@app.route("/register/<role>", methods=['GET', 'POST'])
def register(role="Customer"):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if role == 'Customer':
        form = CustomerRegistrationForm()
    elif role == 'Booking Agent':
        form = BookingAgentRegistrationForm()
    elif role == 'Airline Staff':
        form = AirlineStaffRegistrationForm()
    else:
        return redirect(url_for('login'))

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        if role == 'Customer':
            new_user = Customer(name=form.name.data, email=form.email.data,
                                password=hashed_password)
        elif role == 'Booking Agent':
            agent_id = id_generator()
            new_user = BookingAgent(
                email=form.email.data, password=hashed_password, booking_agent_id=agent_id)
        else:
            new_user = AirlineStaff(
                username=form.username.data, password=hashed_password,
                first_name=form.first_name.data, last_name=form.last_name.data,
                date_of_birth=form.date_of_birth.data,
                airline_name=form.airline_name.data)

        db.session.add(new_user)
        db.session.commit()
        flash(
            f'Your {role} account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login', role=role))

    return render_template('register.html', title='Register', role=role, form=form)


@app.route("/login/", methods=['GET', 'POST'])
@app.route("/login/<role>", methods=['GET', 'POST'])
def login(role="Customer"):
    print(current_user)

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if role == 'Customer':
        form = CustomerLoginForm()
    elif role == 'Booking Agent':
        form = BookingAgentLoginForm()
    elif role == 'Airline Staff':
        form = AirlineStaffLoginForm()
    else:
        return redirect(url_for('login'))

    if form.validate_on_submit():
        if role == "Customer":
            user = Customer.query.filter_by(email=form.email.data).first()
        elif role == "Booking Agent":
            user = BookingAgent.query.filter_by(email=form.email.data).first()
        elif role == "Airline Staff":
            user = AirlineStaff.query.filter_by(
                username=form.username.data).first()
        else:
            return redirect(url_for('login'))

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if there is a next page to be redirected
            next_page = request.args.get('next')
            flash(f" {role} login successful.", "success")

            # return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f"{role} login Unsuccessful.")

    return render_template('login.html', title='Login', role=role, form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash(f'Log out successfully.', 'success')

    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')
