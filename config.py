"""
Configuration settings for the AI-Based Smart Medicine Dispenser
"""
import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    
    # SQLite Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'medicine_dispenser.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    TABLET_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'tablets')
    CAPTURED_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'captures')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # AI Model configuration
    MODEL_PATH = os.path.join(BASE_DIR, 'ml_model', 'tablet_classifier.h5')
    IMAGE_SIZE = (224, 224)
    CONFIDENCE_THRESHOLD = 0.85  # 85% confidence required
    
    # Groq AI Configuration
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY') 
    GROQ_MODEL = 'llama-3.3-70b-versatile'
    
    # Schedule timing slots
    SCHEDULE_SLOTS = {
        'morning': '08:00',
        'afternoon': '13:00',
        'evening': '18:00',
        'night': '21:00'
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
