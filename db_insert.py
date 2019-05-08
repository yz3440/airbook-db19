from airbook import db
from airbook.models import Airline, Airport, Airplane, Flight, Customer, AirlineStaff, AirlineStaffPhoneNumber, BookingAgent, Ticket
db.drop_all()
db.create_all()

# Insert Airline
airlines = []
airlines.append(Airline(name="China Eastern"))
airlines.append(Airline(name="Singapore Airlines"))
airlines.append(Airline(name="Emirates"))
airlines.append(Airline(name="China Southern"))
airlines.append(Airline(name="Lufthansa"))
airlines.append(Airline(name="Delta Air Lines"))

for airline in airlines:
    db.session.add(airline)

# Insert Airport
airports = []
airports.append(Airport(name='PVG', city='Shanghai', country='China'))
airports.append(Airport(name='JFK', city='New York City',
                        country='United State of America'))
airports.append(Airport(name='FRA', city='Frankfurt', country='Germany'))

for airport in airports:
    db.session.add(airport)

# Insert Airplane
airplanes = []
airplanes.append(
    Airplane(id='A380', num_of_seats=525, airline_name="Emirates"))
airplanes.append(
    Airplane(id='A320', num_of_seats=122, airline_name="China Eastern"))
airplanes.append(
    Airplane(id='B747A', num_of_seats=366, airline_name="Lufthansa"))
airplanes.append(
    Airplane(id='B767A', num_of_seats=354, airline_name="Delta Air Lines"))

for airplane in airplanes:
    db.session.add(airplane)

# Insert Flight
flights = []
flights.append(Flight(airline_name='China Eastern', flight_number="CE001",
                      base_price=1234, airplane_id='A320', status='On-Time',
                      departure_airport="PVG", departure_datetime="2019-04-20 12:12:00",
                      arrival_airport="JFK", arrival_datetime="2019-04-21 00:12:00"))
flights.append(Flight(airline_name='Delta Air Lines', flight_number="DAL004",
                      base_price=1200, airplane_id='B767A', status='Delayed',
                      departure_airport="JFK", departure_datetime="2019-01-24 13:12:00",
                      arrival_airport="PVG", arrival_datetime="2019-01-25 01:12:00"))
flights.append(Flight(airline_name='Lufthansa', flight_number="LF127",
                      base_price=800, airplane_id='B747A', status='Delayed',
                      departure_airport="FRA", departure_datetime="2019-03-10 07:08:00",
                      arrival_airport="JFK", arrival_datetime="2019-03-10 13:09:00"))

for flight in flights:
    db.session.add(flight)

# Insert Customer
customers = []
customers.append(Customer(name="Joseph Joestar",
                          email='jojo2nd@jojo.com', password='hamonOverDrive'))
for customer in customers:
    db.session.add(customer)

db.session.commit()
