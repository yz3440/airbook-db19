from flask import render_template, flash, redirect, url_for, request
from airbook import app, db, bcrypt
from airbook.forms import CustomerRegistrationForm, CustomerLoginForm, CustomerEditForm
from airbook.forms import BookingAgentRegistrationForm, BookingAgentLoginForm
from airbook.forms import AirlineStaffRegistrationForm, AirlineStaffLoginForm
from airbook.forms import SearchFlightForm, PaymentForm, AgentPaymentForm, DateRangeSelectionForm
from airbook.forms import FlightStatusEditForm, FlightRegistrationForm, AirplaneRegistrationForm, AirportRegistrationForm
from airbook.models import Airline, Airport, Airplane, Flight, Customer, AirlineStaff, AirlineStaffPhoneNumber, BookingAgent, Ticket
from flask_login import login_user, logout_user, current_user, login_required
from airbook.utils import id_generator, init_dict_key_month_between, str_year_month, top_customer_data_from_tickets, top_booking_agent_data_from_tickets, frequent_customer_data_from_tickets
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func


@app.route("/", methods=['GET', 'POST'])
@app.route("/search_flight", methods=['GET', 'POST'])
def home():
    print(current_user)

    flights = Flight.query.filter(
        Flight.departure_datetime > datetime.utcnow()).order_by(Flight.departure_datetime).all()
    returning_flights = []
    searching = False
    round_trip = False
    form = SearchFlightForm()
    if form.validate_on_submit():
        searching = True
        departure_airport_names = [airport.name for airport in Airport.query.filter(
            or_(Airport.name == form.source_place.data, Airport.city == form.source_place.data)).all()]
        arrival_airport_names = [airport.name for airport in Airport.query.filter(
            or_(Airport.name == form.destination_place.data, Airport.city == form.destination_place.data)).all()]
        flights = Flight.query.filter(
            Flight.departure_airport.in_(departure_airport_names),
            Flight.arrival_airport.in_(arrival_airport_names),
            func.DATE(Flight.departure_datetime) == form.departure_date.data).all()
        departure_date = form.departure_date.data
        if form.round_trip.data:
            returning_flights = Flight.query.filter(
                Flight.arrival_airport.in_(departure_airport_names),
                Flight.departure_airport.in_(arrival_airport_names),
                func.DATE(Flight.arrival_datetime) == form.arrival_date.data).all()
            print(returning_flights)
            arrival_date = form.arrival_date.data
            round_trip = True

    return render_template('search_flight.html', title="Search Result", flights=flights, returning_flights=returning_flights, searching=searching,
                           round_trip=round_trip, form=form)


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

            return redirect(next_page) if next_page else redirect(url_for('account'))
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
    if current_user.role == 'Airline Staff':
        flights = [flight for flight in Flight.query.filter_by(airline_name=current_user.airline_name).all(
        ) if flight.departure_datetime > datetime.utcnow() and flight.departure_datetime < datetime.utcnow() + timedelta(days=30)]
        flights.sort(
            key=lambda flight: flight.departure_datetime, reverse=True)
        return render_template('account.html', flights=flights, title='Account')

    def ticket_departure_datetime(ticket):
        return ticket.flight.departure_datetime
    tickets = [
        ticket for ticket in current_user.tickets if ticket.flight.departure_datetime > datetime.utcnow()]
    tickets.sort(key=ticket_departure_datetime)

    return render_template('account.html', tickets=tickets, title='Account')


@app.route("/my_flights", methods=['GET', 'POST'])
@login_required
def my_flights():
    to_date, from_date = None, None
    searching = False
    form = DateRangeSelectionForm()

    if form.validate_on_submit():
        searching = True
        from_date = form.from_date.data
        to_date = form.to_date.data

    if current_user.role == "Airline Staff":
        airline_name = current_user.airline_name
        flights = Flight.query.filter_by(airline_name=airline_name).all()
        if searching:
            flights = [flight for flight in flights
                       if flight.departure_datetime.date() <= to_date and flight.departure_datetime.date() >= from_date]
        flights.sort(
            key=lambda flight: flight.departure_datetime, reverse=True)
        return render_template('my_flights.html', flights=flights, form=form, searching=searching, title='My Flights')

    tickets = current_user.tickets
    if searching:
        if current_user.role == 'Customer':
            tickets = [ticket for ticket in tickets
                       if ticket.flight.departure_datetime.date() <= to_date and ticket.flight.departure_datetime.date() >= from_date]
            tickets.sort(
                key=lambda ticket: ticket.flight.departure_datetime, reverse=True)
        elif current_user.role == 'Booking Agent':
            tickets = [ticket for ticket in tickets
                       if ticket.purchase_datetime.date() <= to_date and ticket.purchase_datetime.date() >= from_date]
            tickets.sort(
                key=lambda ticket: ticket.purchase_datetime, reverse=True)

    return render_template('my_flights.html', tickets=tickets, form=form, searching=searching, title='My Flights')


@app.route('/account/edit', methods=['GET', 'POST'])
@login_required
def edit_account():
    if current_user.role == 'Customer':
        form = CustomerEditForm()
    else:
        flash(f'Profile update is not available for {current_user.role}.')
        return redirect(url_for("account"))
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.address_building_number = form.address_building_number.data
        current_user.address_street = form.address_street.data
        current_user.address_city = form.address_city.data
        current_user.address_state = form.address_state.data
        current_user.phone_number = form.phone_number.data
        current_user.passport_number = form.passport_number.data
        current_user.passport_expiration = form.passport_expiration.data
        current_user.passport_country = form.passport_country.data
        current_user.date_of_birth = form.date_of_birth.data

        db.session.commit()
        flash("Your account has been updated.")
        return redirect(url_for('account'))

    return render_template('edit_account.html', form=form, title='Account')


@app.route('/view_ticket/<ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    print(ticket)
    if ticket:
        if (current_user.role == 'Customer' and ticket.customer_email == current_user.email) \
                or current_user.role == 'Booking Agent' and ticket.booking_agent_id == current_user.booking_agent_id:
            return render_template('view_ticket.html', ticket=ticket, title='View Ticket')

    flash('You are not able to view this ticket.')
    return redirect(url_for('account'))


@app.route('/purchase/<flight>', methods=['GET', 'POST'])
@login_required
def purchase(flight):
    if current_user.role not in ['Customer', 'Booking Agent']:
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("home"))

    airline_name, flight_number = flight.split('-')

    flight = Flight.query.filter_by(
        airline_name=airline_name, flight_number=flight_number).first()
    flights = [flight]

    if current_user.role == 'Customer':
        form = PaymentForm()
    elif current_user.role == 'Booking Agent':
        form = AgentPaymentForm()

    if form.validate_on_submit():
        for flight in flights:
            ticket = Ticket(airline_name=flight.airline_name, flight_number=flight.flight_number, sold_price=flight.base_price,
                            payment_card_type=form.payment_card_type.data, payment_card_number=form.payment_card_number.data,
                            payment_card_name=form.payment_card_name.data, payment_expiration_date=form.payment_expiration_date.data)
            if current_user.role == 'Customer':
                ticket.customer_email = current_user.email
            elif current_user.role == 'Booking Agent':
                ticket.customer_email = form.customer_email.data
                ticket.booking_agent_id = current_user.booking_agent_id

            db.session.add(ticket)
        db.session.commit()
        flash(f'Purchase Successfully.')
        return redirect(url_for('account'))
    # return redirect(url_for('home'))
    return render_template('purchase.html', form=form, flights=flights, title='Purchase')


@app.route('/view_commision', methods=['GET', 'POST'])
@login_required
def view_commision():
    if current_user.role != 'Booking Agent':
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("home"))

    from_date = datetime.utcnow().date() - timedelta(days=30)
    to_date = datetime.utcnow().date()
    searching = False
    form = DateRangeSelectionForm()

    if form.validate_on_submit():
        searching = True
        from_date = form.from_date.data
        to_date = form.to_date.data

    tickets = [ticket for ticket in current_user.tickets
               if ticket.purchase_datetime.date() <= to_date and ticket.purchase_datetime.date() >= from_date]
    total_commision = sum([ticket.commision for ticket in tickets])
    num_of_tickets = len(tickets)

    return render_template('view_commision.html', num_of_tickets=num_of_tickets,
                           total_commision=total_commision, searching=searching,
                           form=form, title='View Commision')


@app.route('/view_spending', methods=['GET', 'POST'])
@login_required
def view_spending():
    if current_user.role != 'Customer':
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("home"))

    from_date = datetime.utcnow().date() - timedelta(days=365)
    to_date = datetime.utcnow().date()
    searching = False
    form = DateRangeSelectionForm()

    if form.validate_on_submit():
        searching = True
        from_date = form.from_date.data
        to_date = form.to_date.data

    tickets = [ticket for ticket in current_user.tickets
               if ticket.purchase_datetime.date() <= to_date and ticket.purchase_datetime.date() >= from_date]
    total_spending = sum([ticket.sold_price for ticket in tickets])
    num_of_tickets = len(tickets)

    barChartData = init_dict_key_month_between(from_date, to_date)

    for ticket in tickets:
        year_month = str_year_month(ticket.purchase_datetime)
        barChartData[year_month] += ticket.sold_price

    labels, data = [], []
    for label, value in barChartData.items():
        labels.append(label)
        data.append(float(value))

    return render_template('view_spending.html', num_of_tickets=num_of_tickets,
                           total_spending=total_spending, searching=searching,
                           form=form, labels=labels, data=data, title='View Spending')


@app.route('/view_top_customer', methods=['GET', 'POST'])
@login_required
def view_top_customer():
    if current_user.role != 'Booking Agent':
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("home"))

    tickets_one_year = [ticket for ticket in current_user.tickets
                        if ticket.purchase_datetime <= datetime.utcnow() and ticket.purchase_datetime >= datetime.utcnow()-timedelta(days=365)]
    customers, commision, num_of_tickets = top_customer_data_from_tickets(tickets_one_year)
    top_data_one_year = {'customers':customers,'commision':commision,'num_of_tickets':num_of_tickets}

    tickets_six_month = [ticket for ticket in tickets_one_year
                        if ticket.purchase_datetime >= datetime.utcnow()-timedelta(days=183)]
    customers, commision, num_of_tickets = top_customer_data_from_tickets(tickets_six_month)
    top_data_six_month = {'customers':customers,'commision':commision,'num_of_tickets':num_of_tickets}


    return render_template('view_top_customer.html',
            top_data_one_year=top_data_one_year,top_data_six_month=top_data_six_month,
            title='View Commision')


@app.route('/create_flight', methods=['GET', 'POST'])
@login_required
def create_flight():
    if current_user.role in ['Customer', 'Booking Agent']:
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("account"))

    form = FlightRegistrationForm()
    form.airplane_id.choices = [(a.id, a.id)
                                for a in current_user.airline.airplanes]
    form.set_airline_name(current_user.airline_name)

    if form.validate_on_submit():
        flight = Flight(airline_name=current_user.airline_name, airplane_id=form.airplane_id.data,
                        flight_number=form.flight_number.data,
                        base_price=form.base_price.data, status="On-Time",
                        departure_airport=form.departure_airport.data, arrival_airport=form.arrival_airport.data,
                        departure_datetime=form.departure_datetime.data, arrival_datetime=form.arrival_datetime.data)
        db.session.add(flight)
        db.session.commit()
        return redirect(url_for('account'))

    return render_template("create_flight.html", form=form, title='Create Flight')


@app.route('/edit_flight/<flight>', methods=['GET', 'POST'])
@login_required
def edit_flight(flight):
    if current_user.role in ['Customer', 'Booking Agent']:
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("account"))
    airline_name, flight_number = flight.split('-')
    flight = Flight.query.filter_by(
        airline_name=airline_name, flight_number=flight_number).first()
    if flight.airline_name != current_user.airline_name:
        flash(f'You are not authorized to edit this flight.')
        return redirect(url_for("account"))
    else:
        form = FlightStatusEditForm()
        if form.validate_on_submit():
            flight.status = form.status.data
            db.session.commit()
            return redirect(url_for('account'))

        # if flight.status != 'Delayed':
        #     form.status.default = 1
        return render_template("edit_flight.html", flight=flight, form=form, title='Edit Flight')


@app.route('/airplane_management', methods=['GET', 'POST'])
@login_required
def airplane_management():
    if current_user.role in ['Customer', 'Booking Agent']:
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("account"))

    form = AirplaneRegistrationForm()
    form.set_airline_name(current_user.airline_name)

    if form.validate_on_submit():
        airplane = Airplane(id=form.airplane_id.data,
                            airline_name=current_user.airline_name,
                            num_of_seats=form.num_of_seats.data)
        db.session.add(airplane)
        db.session.commit()

    airplanes = Airplane.query.filter_by(
        airline_name=current_user.airline_name).all()

    return render_template("airplane_management.html", airplanes=airplanes, form=form, title='Airplane Management')


@app.route('/airport_management', methods=['GET', 'POST'])
@login_required
def airport_management():
    if current_user.role in ['Customer', 'Booking Agent']:
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("account"))

    form = AirportRegistrationForm()

    if form.validate_on_submit():
        airport = Airport(name=form.name.data,
                          city=form.city.data,
                          country=form.country.data)
        db.session.add(airport)
        db.session.commit()

    airports = Airport.query.all()
    airports.sort(key=lambda airport: airport.country + airport.city)

    return render_template("airport_management.html", airports=airports, form=form, title='Airplane Management')

@app.route('/view_top_booking_agent')
@login_required
def view_top_booking_agent():
    if current_user.role != 'Airline Staff':
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("home"))
    tickets_one_year = Ticket.query.filter(and_(
        Ticket.purchase_datetime <= datetime.utcnow(),
        Ticket.purchase_datetime >= datetime.utcnow()-timedelta(days=365)),
        Ticket.booking_agent_id != None,
        Ticket.airline_name == current_user.airline_name
        ).all()
    booking_agents, commision, num_of_tickets = top_booking_agent_data_from_tickets(tickets_one_year)

    top_data = {'booking_agents':booking_agents,'commision':commision,'num_of_tickets':num_of_tickets}

    return render_template('view_top_booking_agent.html',
            top_data=top_data,
            title='View Commision')


@app.route('/view_frequent_customer')
@login_required
def view_frequent_customer():
    if current_user.role != 'Airline Staff':
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("home"))
    tickets_one_year = Ticket.query.filter(and_(
        Ticket.purchase_datetime <= datetime.utcnow(),
        Ticket.purchase_datetime >= datetime.utcnow()-timedelta(days=365)),
        Ticket.airline_name == current_user.airline_name
        ).all()
    customers, num_of_tickets = frequent_customer_data_from_tickets(tickets_one_year)

    top_data = {'customers':customers, 'num_of_tickets':num_of_tickets}

    tickets = Ticket.query.all()
    customer_airlines={}

    for ticket in tickets:
        if ticket.customer_email not in customer_airlines:
            customer_airlines[ticket.customer_email] = (ticket.airline_name,)
        else:
            if ticket.airline_name not in  customer_airlines[ticket.customer_email]:
                customer_airlines[ticket.customer_email] += (ticket.airline_name,)

    for customer in list(customer_airlines.keys()):
        if len(customer_airlines[customer]) != 1:
             customer_airlines.pop(customer)


    return render_template('view_frequent_customer.html',
            top_data=top_data, customer_airlines=customer_airlines,
            title='View Frequent Customer')

@app.route('/view_ticket_report', methods=['GET', 'POST'])
@login_required
def view_ticket_report():
    if current_user.role != 'Airline Staff':
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("home"))

    from_date = datetime.utcnow() - timedelta(days=365)
    to_date = datetime.utcnow()
    searching = False
    form = DateRangeSelectionForm()

    if form.validate_on_submit():
        searching = True
        from_date = form.from_date.data
        to_date = form.to_date.data

    tickets = Ticket.query.filter(
        Ticket.purchase_datetime <= to_date,
        Ticket.purchase_datetime >= from_date,
        Ticket.airline_name == current_user.airline_name
    ).all()

    barChartData = init_dict_key_month_between(from_date, to_date)
    total_revenue = 0
    num_of_tickets = 0

    for ticket in tickets:
        year_month = str_year_month(ticket.purchase_datetime)
        barChartData[year_month] += 1
        total_revenue += (ticket.sold_price - ticket.commision)
        num_of_tickets += 1


    labels, data = [], []
    for label, value in barChartData.items():
        labels.append(label)
        data.append(float(value))

    return render_template('view_ticket_report.html', searching=searching,
                           form=form, labels=labels,
                           num_of_tickets=num_of_tickets, total_revenue=total_revenue,
                           data=data, title='View Ticket Report')

@app.route('/view_revenue_composition', methods=['GET', 'POST'])
@login_required
def view_revenue_composition():
    if current_user.role != 'Airline Staff':
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("home"))

    from_date = datetime.utcnow() - timedelta(days=365)
    to_date = datetime.utcnow()
    searching = False
    form = DateRangeSelectionForm()

    if form.validate_on_submit():
        searching = True
        from_date = form.from_date.data
        to_date = form.to_date.data

    tickets = Ticket.query.filter(
        Ticket.purchase_datetime <= to_date,
        Ticket.purchase_datetime >= from_date,
        Ticket.airline_name == current_user.airline_name
    ).all()

    direct_sales = 0
    indirect_sales = 0

    for ticket in tickets:
        if ticket.booking_agent_id:
            indirect_sales += ticket.sold_price-ticket.commision
        else:
            direct_sales += ticket.sold_price

    return render_template('view_revenue_composition.html', searching=searching,
                           form=form, direct_sales=direct_sales,
                           indirect_sales=indirect_sales,
                            title='View Revenue Composition')


@app.route('/view_top_destination', methods=['GET', 'POST'])
@login_required
def view_top_destination():
    if current_user.role != 'Airline Staff':
        flash(f'This page is not available for {current_user.role}')
        return redirect(url_for("home"))

    from_date = datetime.utcnow() - timedelta(days=365)
    to_date = datetime.utcnow()
    searching = False
    form = DateRangeSelectionForm()

    if form.validate_on_submit():
        searching = True
        from_date = form.from_date.data
        to_date = form.to_date.data

    tickets = Ticket.query.filter(
        Ticket.purchase_datetime <= to_date,
        Ticket.purchase_datetime >= from_date,
    ).all()

    destination_airports = [ticket.flight.arrival_airport for ticket in tickets]
    destinations = [Airport.query.get(airport_name).city for airport_name in destination_airports]
    destinations_count = {}
    for destination in destinations:
        if destination in destinations_count:
            destinations_count[destination] += 1
        else:
            destinations_count[destination] = 1

    top_three_destinations = (sorted(destinations_count,
                            key=destinations_count.__getitem__, reverse=True))[:3]
    top_three_ticket_count = [destinations_count[destination] for destination in top_three_destinations]


    return render_template('view_top_destination.html', searching=searching,
                           form=form, top_three_destinations=top_three_destinations,
                           top_three_ticket_count=top_three_ticket_count,
                            title='View Top Destination')