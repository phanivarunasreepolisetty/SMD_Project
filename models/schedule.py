"""
Schedule Model
Represents daily medication schedule entries
"""
from datetime import datetime, date, time
from models import db


class Schedule(db.Model):
    """Schedule model for tracking daily medicine intake times"""
    
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    
    scheduled_date = db.Column(db.Date, nullable=False, default=date.today)
    scheduled_time = db.Column(db.Time, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)  # morning, afternoon, evening, night
    
    # Status: pending, taken, missed, wrong_attempt
    status = db.Column(db.String(20), default='pending')
    actual_time = db.Column(db.DateTime, nullable=True)  # When medicine was actually taken
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    
    @staticmethod
    def create_daily_schedule(patient_id, medicine):
        """Create schedule entries for a medicine for today"""
        from config import Config
        
        today = date.today()
        schedules = []
        
        timing_slots = medicine.get_timing_slots()
        
        # Simplified time lookup based on updated Medicine model
        slot_times = {
            'morning': medicine.morning_time,
            'afternoon': medicine.afternoon_time,
            'evening': medicine.evening_time,
            'night': medicine.night_time
        }
        
        for slot in timing_slots:
            # Check if schedule already exists
            existing = Schedule.query.filter_by(
                patient_id=patient_id,
                medicine_id=medicine.id,
                scheduled_date=today,
                time_slot=slot
            ).first()
            
            if not existing:
                custom_time = slot_times.get(slot)
                
                # If custom_time is None (should not happen with default model values)
                if not custom_time:
                    defaults = {
                        'morning': time(8, 0),
                        'afternoon': time(13, 0),
                        'evening': time(18, 0),
                        'night': time(21, 0)
                    }
                    custom_time = defaults.get(slot, time(8, 0))

                schedule = Schedule(
                    patient_id=patient_id,
                    medicine_id=medicine.id,
                    scheduled_date=today,
                    scheduled_time=custom_time,
                    time_slot=slot,
                    status='pending'
                )
                schedules.append(schedule)
        
        return schedules
    
    def mark_as_taken(self):
        """Mark this schedule entry as taken"""
        self.status = 'taken'
        self.actual_time = datetime.utcnow()
    
    def mark_as_missed(self):
        """Mark this schedule entry as missed"""
        self.status = 'missed'
    
    def mark_wrong_attempt(self):
        """Mark a wrong tablet attempt"""
        self.status = 'wrong_attempt'
    
    def get_time_display(self):
        """Get formatted time string"""
        return self.scheduled_time.strftime('%I:%M %p')
    
    def is_overdue(self):
        """Check if this schedule is past due"""
        now = datetime.now()
        scheduled_datetime = datetime.combine(self.scheduled_date, self.scheduled_time)
        return now > scheduled_datetime and self.status == 'pending'
    
    def __repr__(self):
        return f'<Schedule {self.medicine.name} @ {self.scheduled_time}>'
