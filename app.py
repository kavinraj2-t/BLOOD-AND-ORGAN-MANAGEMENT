from flask import Flask,render_template,request,flash,redirect,url_for
from models import db,Details,hdetails,bdetails,Admin
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user


app = Flask(__name__)
app.secret_key = '12345678'

app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:Kav-1908@localhost:3306/hospital_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)
migrate=Migrate(app,db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            flash('✅ Logged in successfully.')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('❌ Invalid username or password.')
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash("✅ Logged out successfully.")
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/hospitals/pending')
@login_required
def pending_hospitals():
    data = hdetails.query.filter_by(is_approved=False).all()
    return render_template('admin_pending_hospitals.html', hdata=data)

@app.route('/admin/bloodbanks/pending')
@login_required
def pending_bloodbanks():
    data = bdetails.query.filter_by(is_approved=False).all()
    return render_template('admin_pending_bloodbanks.html', bdata=data)

@app.route('/admin/hospitals/approve/<int:id>', methods=['POST'])
@login_required
def approve_hospital(id):
    hospital = hdetails.query.get_or_404(id)
    hospital.is_approved = True
    hospital.status = 'Approved'
    db.session.commit()
    flash('✅ Hospital approved successfully!')
    return redirect(url_for('pending_hospitals'))


@app.route('/admin/hospitals/reject/<int:id>', methods=['POST'])
@login_required
def reject_hospital(id):
    hospital = hdetails.query.get_or_404(id)
    hospital.is_approved = False
    hospital.status = 'Rejected'
    db.session.commit()
    flash('❌ Hospital rejected.')
    return redirect(url_for('pending_hospitals'))

@app.route('/admin/bloodbanks/approve/<int:id>', methods=['POST'])
@login_required
def approve_bloodbank(id):
    bloodbank = bdetails.query.get_or_404(id)
    bloodbank.is_approved = True
    bloodbank.status = 'Approved'
    db.session.commit()
    flash('✅ Blood bank approved successfully!')
    return redirect(url_for('pending_bloodbanks'))


@app.route('/admin/bloodbanks/reject/<int:id>', methods=['POST'])
@login_required
def reject_bloodbank(id):
    bloodbank = bdetails.query.get_or_404(id)
    bloodbank.is_approved = False
    bloodbank.status = 'Rejected'
    db.session.commit()
    flash('❌ Blood bank rejected.')
    return redirect(url_for('pending_bloodbanks'))

@app.route('/admin/hospitals/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_hospital(id):
    hospital = hdetails.query.get_or_404(id)
    if request.method == 'POST':
        hospital.hospitalname = request.form['hospital_name']
        hospital.Location = request.form['location']
        hospital.contactno = request.form['contact_no']
        hospital.organs = ','.join(request.form.getlist('organs'))
        db.session.commit()
        flash("✅ Hospital details updated!")
        return redirect(url_for('pending_hospitals'))
    return render_template('edit_hospital.html', hospital=hospital)


@app.route('/admin/bloodbanks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_bloodbank(id):
    bloodbank = bdetails.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['bloodbanksname']
        location = request.form['location']
        contact = request.form['contact_no']
        bloods = request.form.getlist('bloodGroup')
        if not name or not location or not contact or len(bloods) == 0:
            flash("❌ Please fill all fields!", "error")
            return render_template('edit_bloodbank.html', bloodbank=bloodbank)
        bloodbank.bloodbankname = name
        bloodbank.Location = location
        bloodbank.contactno = contact
        bloodbank.bloods = ','.join(bloods)
        try:
            db.session.commit()
            flash("✅ Blood Bank details updated successfully!", "success")
            return redirect(url_for('pending_bloodbanks'))
        except IntegrityError:
            db.session.rollback()
            flash("❌ Contact number already exists. Please use a unique number.", "error")
    
    return render_template('edit_bloodbank.html', bloodbank=bloodbank)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        mobileno=request.form['MobileNo']
        new_detail = Details(name=request.form['name'],blood_group=request.form['bloodGroup'],age=request.form['age'],Gender=request.form['Gender'],mobileno=mobileno,Location=request.form['Location'])
        db.session.add(new_detail)
        try:
           db.session.commit()
           flash("✅ User registered successfully!")
        except IntegrityError:
           db.session.rollback()
           flash("❌ Mobile number already exists. Please use a unique number.")
        return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/bloodbanks/add',methods=['GET','POST'])
def add_bloodbank():
    if request.method == 'POST':
        name = request.form['bloodbanksname']
        location = request.form['location']
        contact = request.form['contact_no']
        bloods=request.form.getlist('bloodGroup')
        if not name or not location or not contact or len(bloods)==0:
            flash("❌ Please fill all the fields!","error")
            return render_template('addbloodbank.html')
        bloods_com=','.join(bloods)
        new_blood = bdetails(bloodbankname=name, Location=location, contactno=contact,bloods=bloods_com,is_approved=False)
        db.session.add(new_blood)
        try:
           db.session.commit()
           flash("✅ Blood Bank registered successfully!")
        except IntegrityError:
           db.session.rollback()
           flash("❌ Contact number already exists. Please use a unique number.")
        return redirect(url_for('add_bloodbank'))


    return render_template('addbloodbank.html')

@app.route('/bloodbanks')
def bloodbanks():
    data=bdetails.query.filter_by(is_approved=True).all()
    return render_template('bloodbanks.html',bdata=data)

@app.route('/hospitals/add',methods=['GET','POST'])
def add_hospital():
    if request.method == 'POST':
        name = request.form['hospital_name']
        location = request.form['location']
        contact = request.form['contact_no']
        Organs=request.form.getlist('organs')
        if not name or not location or not contact or len(Organs)==0:
            db.session.rollback()
            flash("❌ Please fill all the fields")
            return render_template('addhospital.html')
        Organs_com=','.join(Organs)
        new_hospital = hdetails(hospitalname=name, Location=location, contactno=contact,organs=Organs_com,is_approved=False)
        db.session.add(new_hospital)
        try:
           db.session.commit()
           flash("✅ Blood Bank registered successfully!")
        except IntegrityError:
           db.session.rollback()
           flash("❌ Contact number already exists. Please use a unique number.")
        return redirect(url_for('add_hospital'))

    return render_template('addhospital.html')


@app.route('/hospitals')
def hospitals():
    data = hdetails.query.filter_by(is_approved=True).all()
    return render_template('hospitals.html',hdata=data)

@app.route('/donors')
def donors():
    n_details=Details.query.all()
    return render_template('donors.html',detail=n_details)
@app.route('/hospitals/del/<int:Sno>')
@login_required
def delete(Sno):
    data=bdetails.query.get(Sno)
    db.session.delete(data)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)