"""
TabletImage Model
Stores tablet images for AI training dataset
"""
from datetime import datetime
from models import db


class TabletImage(db.Model):
    """TabletImage model for storing training dataset images"""
    
    __tablename__ = 'tablet_images'
    
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # Relative path to image file
    original_filename = db.Column(db.String(255), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_training = db.Column(db.Boolean, default=True)  # Whether used for training
    
    def get_full_path(self):
        """Get full filesystem path to image"""
        import os
        from config import Config
        return os.path.join(Config.UPLOAD_FOLDER, self.image_path)
    
    def __repr__(self):
        return f'<TabletImage {self.id} for Medicine {self.medicine_id}>'
