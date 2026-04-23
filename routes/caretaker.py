"""
Caretaker Routes
All caretaker functionality: authentication, dashboard, patient/medicine management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime, timedelta
from models import db
from models.caretaker import Caretaker
from models.patient import Patient
from models.medicine import Medicine
from models.schedule import Schedule
from models.tablet_image import TabletImage
from models.log import Log
import os
from werkzeug.utils import secure_filename

from config import Config
from datetime import time as time_obj # Rename to avoid conflict if needed, or just use datetime.time

caretaker_bp = Blueprint('caretaker', __name__, url_prefix='/caretaker')


# ============== Authentication Routes ==============

@caretaker_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Caretaker registration"""
    if current_user.is_authenticated:
        return redirect(url_for('caretaker.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('caretaker/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('caretaker/register.html')
        
        if Caretaker.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('caretaker/register.html')
        
        # Create caretaker
        caretaker = Caretaker(name=name, email=email, phone=phone)
        caretaker.set_password(password)
        
        db.session.add(caretaker)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('caretaker.login'))
    
    return render_template('caretaker/register.html')


@caretaker_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Caretaker login"""
    if current_user.is_authenticated:
        return redirect(url_for('caretaker.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        caretaker = Caretaker.query.filter_by(email=email).first()
        
        if caretaker and caretaker.check_password(password):
            login_user(caretaker)
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('caretaker.dashboard'))
        
        flash('Invalid email or password.', 'danger')
    
    return render_template('caretaker/login.html')


@caretaker_bp.route('/logout')
@login_required
def logout():
    """Caretaker logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# ============== Dashboard Routes ==============

@caretaker_bp.route('/dashboard')
@login_required
def dashboard():
    """Caretaker dashboard with patient overview"""
    # Get all active patients for this caretaker
    patients = Patient.query.filter_by(caretaker_id=current_user.id, is_active=True).all()
    
    # Today's statistics
    today = date.today()
    total_schedules = 0
    taken_count = 0
    missed_count = 0
    pending_count = 0
    
    for patient in patients:
        schedules = Schedule.query.filter_by(
            patient_id=patient.id,
            scheduled_date=today
        ).all()
        
        for schedule in schedules:
            total_schedules += 1
            if schedule.status == 'taken':
                taken_count += 1
            elif schedule.status == 'missed':
                missed_count += 1
            elif schedule.status == 'pending':
                pending_count += 1
    
    # Recent logs
    recent_logs = Log.query.join(Patient).filter(
        Patient.caretaker_id == current_user.id
    ).order_by(Log.action_time.desc()).limit(10).all()
    
    # Alerts (missed doses and wrong attempts in last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    alerts = Log.query.join(Patient).filter(
        Patient.caretaker_id == current_user.id,
        Log.action_time >= yesterday,
        Log.status.in_(['missed', 'wrong_attempt'])
    ).order_by(Log.action_time.desc()).all()
    
    return render_template('caretaker/dashboard.html',
                         patients=patients,
                         total_schedules=total_schedules,
                         taken_count=taken_count,
                         missed_count=missed_count,
                         pending_count=pending_count,
                         recent_logs=recent_logs,
                         alerts=alerts)


# ============== Patient Management Routes ==============

@caretaker_bp.route('/patients')
@login_required
def patients():
    """List all patients"""
    patients = Patient.query.filter_by(caretaker_id=current_user.id, is_active=True).order_by(Patient.name).all()
    return render_template('caretaker/patients.html', patients=patients)


@caretaker_bp.route('/patient/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """Add new patient"""
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        medical_conditions = request.form.get('medical_conditions')
        pin_code = request.form.get('pin_code')
        
        if not all([name, age, gender]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('caretaker/add_patient.html')
        
        patient = Patient(
            caretaker_id=current_user.id,
            name=name,
            age=int(age),
            gender=gender,
            medical_conditions=medical_conditions,
            pin_code=pin_code
        )
        
        db.session.add(patient)
        db.session.commit()
        
        flash(f'Patient {name} added successfully!', 'success')
        return redirect(url_for('caretaker.patient_detail', id=patient.id))
    
    return render_template('caretaker/add_patient.html')


@caretaker_bp.route('/patient/<int:id>')
@login_required
def patient_detail(id):
    """View patient details"""
    patient = Patient.query.filter_by(id=id, caretaker_id=current_user.id, is_active=True).first_or_404()
    medicines = Medicine.query.filter_by(patient_id=id, is_active=True).all()
    
    # Today's schedule
    today_schedule = Schedule.query.filter_by(
        patient_id=id,
        scheduled_date=date.today()
    ).order_by(Schedule.scheduled_time).all()
    
    # Recent logs
    recent_logs = Log.query.filter_by(patient_id=id).order_by(
        Log.action_time.desc()
    ).limit(5).all()
    
    return render_template('caretaker/patient_detail.html',
                         patient=patient,
                         medicines=medicines,
                         today_schedule=today_schedule,
                         recent_logs=recent_logs)


@caretaker_bp.route('/patient/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    """Edit patient details"""
    patient = Patient.query.filter_by(id=id, caretaker_id=current_user.id, is_active=True).first_or_404()
    
    if request.method == 'POST':
        patient.name = request.form.get('name')
        patient.age = int(request.form.get('age'))
        patient.gender = request.form.get('gender')
        patient.medical_conditions = request.form.get('medical_conditions')
        patient.pin_code = request.form.get('pin_code')
        
        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('caretaker.patient_detail', id=id))
    
    return render_template('caretaker/edit_patient.html', patient=patient)


@caretaker_bp.route('/patient/<int:id>/delete', methods=['POST'])
@login_required
def delete_patient(id):
    """Delete (deactivate) patient"""
    patient = Patient.query.filter_by(id=id, caretaker_id=current_user.id).first_or_404()
    patient.is_active = False
    db.session.commit()
    flash('Patient removed successfully.', 'success')
    return redirect(url_for('caretaker.patients'))


# ============== Medicine Management Routes ==============

@caretaker_bp.route('/patient/<int:patient_id>/medicine/add', methods=['GET', 'POST'])
@login_required
def add_medicine(patient_id):
    """Add medicine to patient"""
    patient = Patient.query.filter_by(id=patient_id, caretaker_id=current_user.id, is_active=True).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name')
        dosage = request.form.get('dosage')
        frequency = request.form.get('frequency')
        instructions = request.form.get('instructions')
        
        # Get timing checkboxes
        morning = 'morning' in request.form
        afternoon = 'afternoon' in request.form
        evening = 'evening' in request.form
        night = 'night' in request.form
        
        if not all([name, dosage, frequency]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('caretaker/add_medicine.html', patient=patient)
        
        if not (morning or afternoon or evening or night):
            flash('Please select at least one timing.', 'danger')
            return render_template('caretaker/add_medicine.html', patient=patient)
        
        # Helper to parse time
        def parse_time(time_str):
            if not time_str: return None
            try:
                t = datetime.strptime(time_str, '%H:%M').time()
                return t
            except ValueError:
                return None

        morning_time = parse_time(request.form.get('morning_time')) if morning else None
        afternoon_time = parse_time(request.form.get('afternoon_time')) if afternoon else None
        evening_time = parse_time(request.form.get('evening_time')) if evening else None
        night_time = parse_time(request.form.get('night_time')) if night else None

        medicine = Medicine(
            patient_id=patient_id,
            name=name,
            dosage=dosage,
            frequency=frequency,
            instructions=instructions,
            morning=morning,
            morning_time=morning_time or time_obj(8, 0),
            afternoon=afternoon,
            afternoon_time=afternoon_time or time_obj(13, 0),
            evening=evening,
            evening_time=evening_time or time_obj(18, 0),
            night=night,
            night_time=night_time or time_obj(21, 0)
        )
        
        db.session.add(medicine)
        db.session.commit()
        
        # Create today's schedule entries
        schedules = Schedule.create_daily_schedule(patient_id, medicine)
        for schedule in schedules:
            db.session.add(schedule)
        db.session.commit()
        
        flash(f'Medicine {name} added successfully!', 'success')
        return redirect(url_for('caretaker.patient_detail', id=patient_id))
    
    return render_template('caretaker/add_medicine.html', patient=patient)


@caretaker_bp.route('/medicine/<int:id>')
@login_required
def medicine_detail(id):
    """View medicine details"""
    medicine = Medicine.query.filter_by(id=id, is_active=True).first_or_404()
    patient = Patient.query.filter_by(id=medicine.patient_id, caretaker_id=current_user.id, is_active=True).first_or_404()
    
    images = TabletImage.query.filter_by(medicine_id=id).all()
    
    return render_template('caretaker/medicine_detail.html',
                         medicine=medicine,
                         patient=patient,
                         images=images)


@caretaker_bp.route('/medicine/<int:id>/upload', methods=['GET', 'POST'])
@login_required
def upload_image(id):
    """Upload tablet image for AI training"""
    medicine = Medicine.query.filter_by(id=id, is_active=True).first_or_404()
    patient = Patient.query.filter_by(id=medicine.patient_id, caretaker_id=current_user.id, is_active=True).first_or_404()
    
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image selected.', 'danger')
            return redirect(request.url)
        
        file = request.files['image']
        
        if file.filename == '':
            flash('No image selected.', 'danger')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            # Create directory for this medicine
            medicine_folder = os.path.join(Config.TABLET_IMAGES_FOLDER, f'medicine_{id}')
            os.makedirs(medicine_folder, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f'{timestamp}_{filename}'
            filepath = os.path.join(medicine_folder, new_filename)
            
            file.save(filepath)
            
            # Save to database
            relative_path = os.path.join('tablets', f'medicine_{id}', new_filename)
            tablet_image = TabletImage(
                medicine_id=id,
                image_path=relative_path,
                original_filename=filename
            )
            db.session.add(tablet_image)
            db.session.commit()
            
            flash('Image uploaded successfully!', 'success')
            return redirect(url_for('caretaker.medicine_detail', id=id))
    
    images = TabletImage.query.filter_by(medicine_id=id).all()
    return render_template('caretaker/upload_image.html',
                         medicine=medicine,
                         patient=patient,
                         images=images)


@caretaker_bp.route('/medicine/<int:id>/delete', methods=['POST'])
@login_required
def delete_medicine(id):
    """Delete (deactivate) medicine"""
    medicine = Medicine.query.get_or_404(id)
    patient = Patient.query.filter_by(id=medicine.patient_id, caretaker_id=current_user.id).first_or_404()
    
    # Soft delete
    medicine.is_active = False
    
    # Delete pending schedules for this medicine
    pending_schedules = Schedule.query.filter_by(
        medicine_id=id,
        status='pending'
    ).all()
    
    for schedule in pending_schedules:
        db.session.delete(schedule)
    
    db.session.commit()
    flash(f'Medicine {medicine.name} removed successfully.', 'success')
    return redirect(url_for('caretaker.patient_detail', id=patient.id))


@caretaker_bp.route('/image/<int:id>/delete', methods=['POST'])
@login_required
def delete_image(id):
    """Delete a tablet training image"""
    image = TabletImage.query.get_or_404(id)
    medicine_id = image.medicine_id
    
    # Verify ownership
    medicine = Medicine.query.get(medicine_id)
    patient = Patient.query.get(medicine.patient_id)
    if patient.caretaker_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('caretaker.dashboard'))

    # Delete file
    try:
        full_path = os.path.join(Config.UPLOAD_FOLDER, image.image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    db.session.delete(image)
    db.session.commit()
    
    flash('Image deleted successfully.', 'success')
    return redirect(url_for('caretaker.upload_image', id=medicine_id))


@caretaker_bp.route('/medicine/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medicine(id):
    """Edit medicine details"""
    medicine = Medicine.query.filter_by(id=id, is_active=True).first_or_404()
    patient = Patient.query.filter_by(id=medicine.patient_id, caretaker_id=current_user.id, is_active=True).first_or_404()
    
    if request.method == 'POST':
        medicine.name = request.form.get('name')
        medicine.dosage = request.form.get('dosage')
        medicine.frequency = request.form.get('frequency')
        medicine.instructions = request.form.get('instructions')
        
        # Update timings
        medicine.morning = 'morning' in request.form
        medicine.afternoon = 'afternoon' in request.form
        medicine.evening = 'evening' in request.form
        medicine.night = 'night' in request.form
        
        def parse_time(time_str):
            if not time_str: return None
            try:
                t = datetime.strptime(time_str, '%H:%M').time()
                return t
            except ValueError:
                return None
        
        if medicine.morning:
            t = parse_time(request.form.get('morning_time'))
            if t: medicine.morning_time = t
            
        if medicine.afternoon:
            t = parse_time(request.form.get('afternoon_time'))
            if t: medicine.afternoon_time = t
            
        if medicine.evening:
            t = parse_time(request.form.get('evening_time'))
            if t: medicine.evening_time = t
            
        if medicine.night:
            t = parse_time(request.form.get('night_time'))
            if t: medicine.night_time = t
            
        if not (medicine.morning or medicine.afternoon or medicine.evening or medicine.night):
             flash('Please select at least one timing.', 'danger')
             return render_template('caretaker/edit_medicine.html', medicine=medicine, patient=patient)

        db.session.commit()
        
        # Regenerate/Update today's schedule? 
        # Ideally we should update pending schedules for today if times changed.
        # For simplicity, we can delete pending ones and recreate them.
        today = date.today()
        pending_schedules = Schedule.query.filter_by(
            medicine_id=id,
            scheduled_date=today,
            status='pending'
        ).all()
        
        for s in pending_schedules:
            db.session.delete(s)
        db.session.commit()
        
        # Create new ones
        new_schedules = Schedule.create_daily_schedule(patient.id, medicine)
        for s in new_schedules:
            db.session.add(s)
        db.session.commit()
        
        flash(f'Medicine {medicine.name} updated successfully!', 'success')
        return redirect(url_for('caretaker.medicine_detail', id=id))

    return render_template('caretaker/edit_medicine.html', medicine=medicine, patient=patient)


# ============== Reports Routes ==============

@caretaker_bp.route('/reports')
@login_required
def reports():
    """Reports and analytics page"""
    patients = Patient.query.filter_by(caretaker_id=current_user.id, is_active=True).all()
    
    # Get patient_id from query params or use first patient
    patient_id = request.args.get('patient_id', type=int)
    selected_patient = None
    report_data = None
    
    if patient_id:
        selected_patient = Patient.query.filter_by(
            id=patient_id, caretaker_id=current_user.id
        ).first()
    elif patients:
        selected_patient = patients[0]
        patient_id = selected_patient.id
    
    if selected_patient:
        # Generate report for last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # Get schedule statistics
        schedules = Schedule.query.filter(
            Schedule.patient_id == patient_id,
            Schedule.scheduled_date >= start_date,
            Schedule.scheduled_date <= end_date
        ).all()
        
        total = len(schedules)
        taken = sum(1 for s in schedules if s.status == 'taken')
        missed = sum(1 for s in schedules if s.status == 'missed')
        wrong = sum(1 for s in schedules if s.status == 'wrong_attempt')
        pending = sum(1 for s in schedules if s.status == 'pending')
        
        compliance_rate = (taken / total * 100) if total > 0 else 0
        
        report_data = {
            'total': total,
            'taken': taken,
            'missed': missed,
            'wrong': wrong,
            'pending': pending,
            'compliance_rate': round(compliance_rate, 1),
            'start_date': start_date,
            'end_date': end_date
        }
        
        # Get detailed logs
        logs = Log.query.filter(
            Log.patient_id == patient_id,
            Log.action_time >= datetime.combine(start_date, datetime.min.time())
        ).order_by(Log.action_time.desc()).all()
        
        report_data['logs'] = logs
    
    return render_template('caretaker/reports.html',
                         patients=patients,
                         selected_patient=selected_patient,
                         report_data=report_data)


# ============== Generate Daily Schedule ==============

@caretaker_bp.route('/generate-schedule')
@login_required
def generate_schedule():
    """Generate today's schedule for all patients"""
    patients = Patient.query.filter_by(caretaker_id=current_user.id, is_active=True).all()
    
    schedule_count = 0
    for patient in patients:
        medicines = Medicine.query.filter_by(patient_id=patient.id, is_active=True).all()
        for medicine in medicines:
            schedules = Schedule.create_daily_schedule(patient.id, medicine)
            for schedule in schedules:
                db.session.add(schedule)
                schedule_count += 1
    
    db.session.commit()
    flash(f'Generated {schedule_count} schedule entries for today.', 'success')
    return redirect(url_for('caretaker.dashboard'))
