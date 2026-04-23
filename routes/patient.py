"""
Patient Routes
Patient login, dashboard, and medicine verification interface
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from datetime import date, datetime
from models import db
from models.patient import Patient
from models.medicine import Medicine
from models.schedule import Schedule
from models.log import Log

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


@patient_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Patient login with simple PIN"""
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        pin_code = request.form.get('pin_code')
        
        patient = Patient.query.filter_by(id=patient_id, is_active=True).first()
        
        if patient:
            # If PIN is set, verify it; otherwise allow access
            if patient.pin_code:
                if patient.pin_code == pin_code:
                    session['patient_id'] = patient.id
                    flash(f'Welcome, {patient.name}!', 'success')
                    return redirect(url_for('patient.dashboard'))
                else:
                    flash('Invalid PIN code.', 'danger')
            else:
                session['patient_id'] = patient.id
                flash(f'Welcome, {patient.name}!', 'success')
                return redirect(url_for('patient.dashboard'))
        else:
            flash('Patient not found.', 'danger')
    
    # Get list of active patients for selection
    patients = Patient.query.filter_by(is_active=True).all()
    return render_template('patient/login.html', patients=patients)


@patient_bp.route('/logout')
def logout():
    """Patient logout"""
    session.pop('patient_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('patient.login'))


def get_current_patient():
    """Get current logged in patient"""
    patient_id = session.get('patient_id')
    if patient_id:
        return Patient.query.get(patient_id)
    return None


@patient_bp.route('/dashboard')
def dashboard():
    """Patient dashboard with today's schedule"""
    patient = get_current_patient()
    if not patient:
        return redirect(url_for('patient.login'))
    
    # Get today's schedule
    today = date.today()
    schedules = Schedule.query.filter_by(
        patient_id=patient.id,
        scheduled_date=today
    ).order_by(Schedule.scheduled_time).all()
    
    # Separate by status
    pending = [s for s in schedules if s.status == 'pending']
    taken = [s for s in schedules if s.status == 'taken']
    missed = [s for s in schedules if s.status == 'missed']
    
    # Calculate current time slot
    now = datetime.now().time()
    current_slot = None
    if now < datetime.strptime('12:00', '%H:%M').time():
        current_slot = 'morning'
    elif now < datetime.strptime('17:00', '%H:%M').time():
        current_slot = 'afternoon'
    elif now < datetime.strptime('20:00', '%H:%M').time():
        current_slot = 'evening'
    else:
        current_slot = 'night'
    
    # Get pending medicine for current slot, ONLY if the scheduled time has arrived
    current_pending = []
    for s in pending:
        if s.time_slot == current_slot and now >= s.scheduled_time:
            current_pending.append(s)
    
    return render_template('patient/dashboard.html',
                         patient=patient,
                         schedules=schedules,
                         pending=pending,
                         taken=taken,
                         missed=missed,
                         current_slot=current_slot,
                         current_pending=current_pending,
                         today=today)


@patient_bp.route('/take-medicine/<int:schedule_id>')
def take_medicine(schedule_id):
    """Medicine verification page with camera"""
    patient = get_current_patient()
    if not patient:
        return redirect(url_for('patient.login'))
    
    schedule = Schedule.query.filter_by(
        id=schedule_id,
        patient_id=patient.id
    ).first_or_404()
    
    medicine = schedule.medicine
    
    return render_template('patient/take_medicine.html',
                         patient=patient,
                         schedule=schedule,
                         medicine=medicine)


@patient_bp.route('/confirm-intake/<int:schedule_id>', methods=['POST'])
def confirm_intake(schedule_id):
    """Manually confirm medicine intake (fallback without AI)"""
    patient = get_current_patient()
    if not patient:
        return redirect(url_for('patient.login'))
    
    schedule = Schedule.query.filter_by(
        id=schedule_id,
        patient_id=patient.id
    ).first_or_404()
    
    # Mark as taken
    schedule.mark_as_taken()
    
    # Create log entry
    log = Log.create_intake_log(
        patient_id=patient.id,
        medicine_id=schedule.medicine_id,
        schedule_id=schedule.id,
        status='taken',
        notes='Manually confirmed by patient'
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Medicine intake recorded successfully!', 'success')
    return redirect(url_for('patient.dashboard'))


@patient_bp.route('/history')
def history():
    """View intake history"""
    patient = get_current_patient()
    if not patient:
        return redirect(url_for('patient.login'))
    
    logs = Log.query.filter_by(patient_id=patient.id).order_by(
        Log.action_time.desc()
    ).limit(50).all()
    
    return render_template('patient/history.html',
                         patient=patient,
                         logs=logs)
