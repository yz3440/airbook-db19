from flask import Flask, render_template, flash, redirect, url_for
from forms import CustomerRegistrationForm, CustomerLoginForm
from datetime import datetime
app = Flask(__name__)

app.config['SECRET_KEY'] = 'ccaeb368bffcc1cf04e27b87bbca191e'

db_string = "postgres://ymudxlljrlnwkt:2217a03b578f151800e10aeacae4ade478eab8025240f266a110bcb1aae425f9@ec2-54-221-201-212.compute-1.amazonaws.com:5432/denqg5recvhr92"

posts = [
    {
        'author': "Cory Hl",
        'title': "Blogt Post 1",
        'content': 'Fist'
    }, {
        'author': "123 Hl",
        'title': "Blogt Post 1",
        'content': '123123'
    }

]

flights = [
    {"departure_datetime": datetime(year=2019, month=5, day=9, hour=22, minute=55),
     "arrival_datetime": datetime(year=2019, month=5, day=11, hour=00, minute=5),
     "airline_name": "Hainan Airline",
     "flight_number": "HU1111",
     "departure_airport": "PVG",
     "arrival_airport": "AUD",
     "base_price": 1000,
     "status": "Delayed"
     }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('search_flights.html', title="Search Result", flights=flights)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = CustomerRegistrationForm()

    if form.validate_on_submit():
        flash(f'Account created for {form.email.data}', 'success')
        return redirect(url_for('home'))

    return render_template('customer_register.html', title='Register', form=form)


@app.route("/login")
def login():
    form = CustomerLoginForm()
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
