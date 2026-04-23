"""
Patient Model
Represents patients who receive medications
"""
from datetime import datetime
from models import db


class Patient(db.Model):
    """Patient model for storing patient information"""
    
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    caretaker_id = db.Column(db.Integer, db.ForeignKey('caretakers.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # Male, Female, Other
    medical_conditions = db.Column(db.Text, nullable=True)
    pin_code = db.Column(db.String(6), nullable=True)  # Simple PIN for patient login
    photo_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    medicines = db.relationship('Medicine', backref='patient', lazy='dynamic')
    schedules = db.relationship('Schedule', backref='patient', lazy='dynamic')
    logs = db.relationship('Log', backref='patient', lazy='dynamic')
    
    def get_today_schedule(self):
        """Get today's medication schedule"""
        from datetime import date
        from models.schedule import Schedule
        return Schedule.query.filter(
            Schedule.patient_id == self.id,
            Schedule.scheduled_date == date.today()
        ).all()
    
    def get_pending_medicines(self):
        """Get pending medicines for today"""
        from datetime import date
        from models.schedule import Schedule
        return Schedule.query.filter(
            Schedule.patient_id == self.id,
            Schedule.scheduled_date == date.today(),
            Schedule.status == 'pending'
        ).all()
    
    def get_compliance_rate(self, days=7):
        """Calculate compliance rate for last N days"""
        from datetime import date, timedelta
        from models.schedule import Schedule
        
        start_date = date.today() - timedelta(days=days)
        total = Schedule.query.filter(
            Schedule.patient_id == self.id,
            Schedule.scheduled_date >= start_date
        ).count()
        
        if total == 0:
            return 100.0
        
        taken = Schedule.query.filter(
            Schedule.patient_id == self.id,
            Schedule.scheduled_date >= start_date,
            Schedule.status == 'taken'
        ).count()
        
        return round((taken / total) * 100, 1)
    
    def __repr__(self):
        return f'<Patient {self.name}>'
