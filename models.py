from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Officer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officer_name = db.Column(db.String(50), unique=True, nullable=False)
    off_pwd = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=2)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)

class Courier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cons_no = db.Column(db.String(15), unique=True, nullable=False)
    
    # Sender Details (Must match init_db.py)
    ship_name = db.Column(db.String(100))
    sender_phone = db.Column(db.String(20)) # This was missing in your old DB
    sender_email = db.Column(db.String(100))
    sender_address = db.Column(db.Text)
    
    # Receiver Details
    rev_name = db.Column(db.String(100))
    receiver_phone = db.Column(db.String(20))
    receiver_email = db.Column(db.String(100))
    receiver_address = db.Column(db.Text)
    
    # Parcel Details
    weight = db.Column(db.Float, default=1.0)
    p_type = db.Column(db.String(50))
    priority = db.Column(db.String(50))
    contents_description = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    no_of_pieces = db.Column(db.Integer, default=1)
    
    cost = db.Column(db.Float)
    est_delivery = db.Column(db.String(50))
    pick_date = db.Column(db.DateTime, default=datetime.utcnow)

class CourierTrack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cons_no = db.Column(db.String(15), db.ForeignKey('courier.cons_no'))
    status = db.Column(db.String(50)) 
    current_city = db.Column(db.String(100))
    comments = db.Column(db.Text)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    message = db.Column(db.Text)
    reply = db.Column(db.Text)
    replied_at = db.Column(db.DateTime)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)