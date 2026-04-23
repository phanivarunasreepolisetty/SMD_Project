"""
Caretaker Model
Represents healthcare providers, family members, or nurses who manage patients
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models import db


class Caretaker(UserMixin, db.Model):
    """Caretaker model for user authentication and patient management"""
    
    __tablename__ = 'caretakers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to patients
    patients = db.relationship('Patient', backref='caretaker', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_patient_count(self):
        """Get number of patients managed by this caretaker"""
        return self.patients.count()
    
    def __repr__(self):
        return f'<Caretaker {self.name}>'
