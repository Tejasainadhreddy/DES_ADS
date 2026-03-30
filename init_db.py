from app import app, db
from models import Officer, User, Courier, CourierTrack
import random, string
from datetime import datetime

with app.app_context():
    db.create_all()
    
    # Super Admin
    if not Officer.query.filter_by(officer_name='Team_7').first():
        db.session.add(Officer(officer_name='Team_7', off_pwd='password7', level=1))
    
    # 10 Sample Users
    sample_users = [
        ("Sriram Kumar", "sriram@csueb.edu", "password123", "510-885-3000", "25800 Carlos Bee Blvd, Hayward, CA"),
        ("Priya Sharma", "priya@gmail.com", "pass123", "510-123-4567", "123 Main St, Oakland, CA"),
        ("Michael Chen", "mchen@outlook.com", "pass123", "510-987-6543", "456 Oak Ave, San Francisco, CA"),
        ("Emma Rodriguez", "emma.r@icloud.com", "pass123", "415-555-1212", "789 Pine St, Berkeley, CA"),
        ("David Patel", "dpatel@yahoo.com", "pass123", "510-222-3333", "101 University Ave, Hayward, CA"),
        ("Sophia Lee", "sophia.lee@gmail.com", "pass123", "510-444-5555", "202 Lakeview Dr, Fremont, CA"),
        ("James Wilson", "james.w@proton.me", "pass123", "415-666-7777", "303 Market St, San Leandro, CA"),
        ("Olivia Garcia", "olivia.g@outlook.com", "pass123", "510-888-9999", "404 Campus Dr, Hayward, CA"),
        ("Liam Thompson", "liam.t@gmail.com", "pass123", "510-111-2222", "505 Redwood Rd, Oakland, CA"),
        ("Isabella Martinez", "isabella.m@icloud.com", "pass123", "415-333-4444", "606 Bayview Ave, San Francisco, CA")
    ]

    for name, email, pwd, phone, addr in sample_users:
        if not User.query.filter_by(email=email).first():
            db.session.add(User(fullname=name, email=email, password=pwd, phone=phone, address=addr))

    # Fix: Re-mapped indices to match Courier Model fields correctly
    if Courier.query.count() < 2:
        sample_orders = [
            ("Sriram Kumar", "510-885-3000", "sriram@csueb.edu", "25800 Carlos Bee Blvd, Hayward, CA",
             "Alice Johnson", "510-111-2222", "alice@gmail.com", "123 Market St, San Francisco, CA",
             3.2, "Box", "Express", "Books and documents", "Handle with care", 1, 58.0),
            
            ("Priya Sharma", "510-123-4567", "priya@gmail.com", "123 Main St, Oakland, CA",
             "Bob Smith", "510-333-4444", "bob@outlook.com", "456 Tech Way, San Jose, CA",
             1.8, "Envelope", "Standard", "Important documents", "", 1, 28.0),
        ]
        for data in sample_orders:
            cid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            c = Courier(
                cons_no=cid,
                ship_name=data[0], sender_phone=data[1], sender_email=data[2], sender_address=data[3],
                rev_name=data[4], receiver_phone=data[5], receiver_email=data[6], receiver_address=data[7],
                weight=data[8], p_type=data[9], priority=data[10],
                contents_description=data[11], special_instructions=data[12],
                no_of_pieces=data[13], cost=data[14],
                est_delivery="In Transit"
            )
            db.session.add(c)
            db.session.add(CourierTrack(cons_no=cid, status="Pickup Requested", current_city=data[3]))

    db.session.commit()
    print("✅ LOG: Database Fixed & Seeded.")