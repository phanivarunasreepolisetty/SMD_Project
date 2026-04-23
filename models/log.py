"""
Log Model
Records all medication-related activities for monitoring
"""
from datetime import datetime
from models import db


class Log(db.Model):
    """Log model for recording medication intake history"""
    
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=True)
    
    scheduled_time = db.Column(db.DateTime, nullable=True)
    action_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status: taken, missed, wrong_attempt, verified
    status = db.Column(db.String(20), nullable=False)
    
    # AI verification details
    predicted_medicine = db.Column(db.String(100), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    captured_image_path = db.Column(db.String(255), nullable=True)
    
    # Additional notes
    notes = db.Column(db.Text, nullable=True)
    
    # Log levels for different event types
    LOG_STATUS = {
        'taken': 'success',
        'missed': 'warning',
        'wrong_attempt': 'danger',
        'verified': 'info'
    }
    
    @staticmethod
    def create_intake_log(patient_id, medicine_id, schedule_id, status, 
                          predicted_medicine=None, confidence=None, image_path=None, notes=None):
        """Create a new log entry for medicine intake"""
        log = Log(
            patient_id=patient_id,
            medicine_id=medicine_id,
            schedule_id=schedule_id,
            status=status,
            predicted_medicine=predicted_medicine,
            confidence_score=confidence,
            captured_image_path=image_path,
            notes=notes
        )
        return log
    
    def get_status_class(self):
        """Get CSS class for status display"""
        return self.LOG_STATUS.get(self.status, 'secondary')
    
    def get_time_display(self):
        """Get formatted action time"""
        return self.action_time.strftime('%I:%M %p, %d %b %Y')
    
    def __repr__(self):
        return f'<Log {self.status} - Patient {self.patient_id}>'
