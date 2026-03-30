from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Courier, CourierTrack, Officer, User, ContactMessage
import random, string
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///team7_logistics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'team7_master_engineering_key_2026'
db.init_app(app)

# Fully random 12-character tracking ID
def gen_id():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=12))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        admin = Officer.query.filter_by(officer_name=u, off_pwd=p).first()
        if admin:
            session.clear()
            session.update({'user': admin.officer_name, 'role': 'admin', 'level': admin.level})
            return redirect(url_for('admin_dashboard'))
            
        user = User.query.filter_by(email=u, password=p).first()
        if user:
            session.clear()
            session.update({'user': user.fullname, 'role': 'user', 'id': user.id})
            return redirect(url_for('user_dashboard'))
            
        flash("Invalid Credentials", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(fullname=request.form.get('fullname'), 
                        email=request.form.get('email'),
                        password=request.form.get('password'), 
                        phone=request.form.get('phone'), 
                        address=request.form.get('address'))
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successful! Please Login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Admin access required", "danger")
        return redirect(url_for('login'))
        
    return render_template('admin_dashboard.html', 
                           couriers=Courier.query.order_by(Courier.pick_date.desc()).all(),
                           messages=ContactMessage.query.order_by(ContactMessage.date_sent.desc()).all(),
                           users=User.query.all(),
                           u_count=User.query.count(),
                           t_orders=Courier.query.count())

@app.route('/user_dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        flash("Please login as a customer", "danger")
        return redirect(url_for('login'))
        
    user = User.query.get(session['id'])
    orders = Courier.query.filter((Courier.ship_name == user.fullname) | 
                                  (Courier.rev_name == user.fullname)).all()
    
    # ✅ FIXED: Now correctly rendering user_dashboard.html
    return render_template('user_dashboard.html', user=user, orders=orders)

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    u = User.query.get(session['id'])
    u.fullname = request.form.get('fullname')
    u.phone = request.form.get('phone')
    u.address = request.form.get('address')
    db.session.commit()
    flash("Profile Updated Successfully!", "success")
    return redirect(url_for('user_dashboard'))

@app.route('/request-pickup', methods=['GET', 'POST'])
def request_pickup():
    if session.get('role') != 'user':
        flash("Please login as a customer", "danger")
        return redirect(url_for('login'))
        
    u = User.query.get(session['id'])
    
    if request.method == 'POST':
        weight_raw = request.form.get('weight')
        try:
            weight = float(weight_raw)
            if weight <= 0 or weight > 1000:
                flash("Please enter a realistic weight (0.1 - 1000kg).", "warning")
                return render_template('request_pickup.html', user=u)
        except:
            flash("Invalid weight format.", "danger")
            return render_template('request_pickup.html', user=u)

        cid = gen_id()
        priority = request.form.get('priority')
        cost = round(12.5 * weight + (20 if priority == 'Express' else 8), 2)
        
        new_c = Courier(
            cons_no=cid,
            ship_name=u.fullname,
            sender_phone=u.phone,
            sender_email=u.email,
            sender_address=u.address,
            rev_name=request.form.get('rev_name'),
            receiver_phone=request.form.get('receiver_phone'),
            receiver_email=request.form.get('receiver_email'),
            receiver_address=request.form.get('receiver_address'),
            weight=weight,
            p_type=request.form.get('p_type'),
            priority=priority,
            contents_description=request.form.get('contents_description'),
            special_instructions=request.form.get('special_instructions'),
            no_of_pieces=int(request.form.get('no_of_pieces', 1)),
            cost=cost,
            est_delivery="Pickup Requested"
        )
        db.session.add(new_c)
        db.session.add(CourierTrack(cons_no=cid, status="Pickup Requested", current_city=u.address))
        db.session.commit()
        flash(f"Pickup Requested Successfully! Tracking ID: {cid}", "success")
        return redirect(url_for('user_dashboard'))
        
    return render_template('request_pickup.html', user=u)

@app.route('/add-courier', methods=['GET', 'POST'])
def add_courier():
    if session.get('role') != 'admin':
        flash("Admin access required", "danger")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        weight_raw = request.form.get('weight')
        try:
            weight = float(weight_raw)
        except:
            flash("Invalid weight.", "danger")
            return render_template('add_courier.html')

        cid = gen_id()
        priority = request.form.get('priority')
        cost = round(12.5 * weight + (20 if priority == 'Express' else 8), 2)
        
        new_c = Courier(
            cons_no=cid,
            ship_name=request.form.get('ship_name'),
            sender_phone=request.form.get('sender_phone'),
            sender_email=request.form.get('sender_email'),
            sender_address=request.form.get('sender_address'),
            rev_name=request.form.get('rev_name'),
            receiver_phone=request.form.get('receiver_phone'),
            receiver_email=request.form.get('receiver_email'),
            receiver_address=request.form.get('receiver_address'),
            weight=weight,
            p_type=request.form.get('p_type'),
            priority=priority,
            contents_description=request.form.get('contents_description'),
            special_instructions=request.form.get('special_instructions'),
            no_of_pieces=int(request.form.get('no_of_pieces', 1)),
            cost=cost,
            est_delivery="Awaiting Approval"
        )
        db.session.add(new_c)
        db.session.add(CourierTrack(cons_no=cid, status="Pickup Requested", current_city=request.form.get('sender_address')))
        db.session.commit()
        flash(f"Shipment Created! Tracking ID: {cid}", "success")
        return render_template('add_courier.html', success_id=cid)
        
    return render_template('add_courier.html')

@app.route('/update-status', methods=['GET', 'POST'])
def update_status():
    if session.get('role') != 'admin':
        flash("Admin access required", "danger")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        cid = request.form.get('cons_no')
        c = Courier.query.filter_by(cons_no=cid).first()
        if c:
            new_track = CourierTrack(cons_no=cid,
                                     status=request.form.get('status'),
                                     current_city=request.form.get('city'),
                                     comments=request.form.get('comments'))
            db.session.add(new_track)
            c.est_delivery = request.form.get('status')
            db.session.commit()
            flash("Shipment status updated successfully!", "success")
            return redirect(url_for('admin_dashboard'))
        flash("Courier not found!", "danger")
        
    cons_no = request.args.get('cons_no', '')
    return render_template('update_status.html', cons_no=cons_no)

@app.route('/track-search', methods=['POST'])
def track_search():
    cid = request.form.get('cons_no')
    shipment = Courier.query.filter_by(cons_no=cid).first()
    updates = CourierTrack.query.filter_by(cons_no=cid).order_by(CourierTrack.update_time.desc()).all()
    if shipment and updates:
        return render_template('track_details.html', shipment=shipment, updates=updates)
    flash("Tracking ID not found or no updates yet.", "danger")
    return redirect(url_for('home'))

@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        db.session.add(ContactMessage(name=request.form.get('name'),
                                      email=request.form.get('email'),
                                      subject=request.form.get('subject'),
                                      message=request.form.get('message')))
        db.session.commit()
        flash("Support Ticket Created. We will get back to you soon!", "success")
        return redirect(url_for('home'))
    return render_template('about.html')

@app.route('/reply-message/<int:msg_id>', methods=['POST'])
def reply_message(msg_id):
    if session.get('role') != 'admin':
        flash("Admin access required", "danger")
        return redirect(url_for('login'))
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.reply = request.form.get('reply')
    msg.replied_at = datetime.utcnow()
    db.session.commit()
    flash("Reply sent successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/customer-care')
def customer_care():
    return render_template('customer_care.html')

@app.route('/services')
def services():
    return render_template('services_page.html')

@app.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    if session.get('role') != 'admin' or session.get('level') != 1:
        flash("Super admin access required", "danger")
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        new_o = Officer(officer_name=request.form.get('username'), 
                        off_pwd=request.form.get('password'), 
                        level=2)
        db.session.add(new_o)
        db.session.commit()
        flash("New backup admin created successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('create_admin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)