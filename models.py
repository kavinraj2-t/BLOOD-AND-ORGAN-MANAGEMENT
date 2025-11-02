from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()
class Details(db.Model):
    Sno=db.Column(db.Integer,primary_key=True)
    blood_group=db.Column(db.String(4),nullable=False)
    name=db.Column(db.String(100),nullable=False)
    age=db.Column(db.Integer,nullable=False)
    Gender=db.Column(db.String(5),nullable=False)
    mobileno=db.Column(db.String(10),unique=True,nullable=False)
    Location=db.Column(db.String(20),nullable=False)

class bdetails(db.Model):
    Sno=db.Column(db.Integer,primary_key=True)
    bloodbankname=db.Column(db.String(100),nullable=False)
    contactno=db.Column(db.String(10),unique=True,nullable=False)
    Location=db.Column(db.String(20),nullable=False)
    bloods=db.Column(db.String(100),nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='Pending',nullable=False)

class hdetails(db.Model):
    Sno=db.Column(db.Integer,primary_key=True)
    hospitalname=db.Column(db.String(100),nullable=False)
    contactno=db.Column(db.String(10),unique=True,nullable=False)
    Location=db.Column(db.String(20),nullable=False)
    organs=db.Column(db.String(100),nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='Pending',nullable=False)

class Admin(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True,nullable=False)
    password_hash = db.Column(db.String(200),nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
            return check_password_hash(self.password_hash, password)
