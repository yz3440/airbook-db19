from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ccaeb368bffcc1cf04e27b87bbca191e'
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://ymudxlljrlnwkt:2217a03b578f151800e10aeacae4ade478eab8025240f266a110bcb1aae425f9@ec2-54-221-201-212.compute-1.amazonaws.com:5432/denqg5recvhr92"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/airbook"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


def get_route():
    from airbook import routes

get_route()
