"""
Medicine Model
Represents prescribed medicines for patients
"""
from datetime import datetime, time
from models import db


class Medicine(db.Model):
    """Medicine model for storing prescription details"""
    
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)  # e.g., "500mg", "10ml"
    frequency = db.Column(db.String(50), nullable=False)  # e.g., "Once daily", "Twice daily"
    instructions = db.Column(db.Text, nullable=True)  # Special instructions
    
    # Timing slots (boolean for each time slot)
    morning = db.Column(db.Boolean, default=False)
    morning_time = db.Column(db.Time, default=time(8, 0))
    
    afternoon = db.Column(db.Boolean, default=False)
    afternoon_time = db.Column(db.Time, default=time(13, 0))
    
    evening = db.Column(db.Boolean, default=False)
    evening_time = db.Column(db.Time, default=time(18, 0))
    
    night = db.Column(db.Boolean, default=False)
    night_time = db.Column(db.Time, default=time(21, 0))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    images = db.relationship('TabletImage', backref='medicine', lazy='dynamic')
    schedules = db.relationship('Schedule', backref='medicine', lazy='dynamic')
    logs = db.relationship('Log', backref='medicine', lazy='dynamic')
    
    def get_timing_slots(self):
        """Get list of active timing slots"""
        slots = []
        if self.morning:
            slots.append('morning')
        if self.afternoon:
            slots.append('afternoon')
        if self.evening:
            slots.append('evening')
        if self.night:
            slots.append('night')
        return slots
    
    def get_timing_display(self):
        """Get human-readable timing string"""
        slots = self.get_timing_slots()
        return ', '.join([s.capitalize() for s in slots])
    
    def get_image_count(self):
        """Get number of training images uploaded"""
        return self.images.count()
    
    def has_sufficient_images(self, min_images=5):
        """Check if enough training images are uploaded"""
        return self.get_image_count() >= min_images
    
    def __repr__(self):
        return f'<Medicine {self.name} ({self.dosage})>'
