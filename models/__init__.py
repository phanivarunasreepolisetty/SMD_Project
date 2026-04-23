"""
Database Models Package
Initializes SQLAlchemy and exports all models
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import all models for easy access
from models.caretaker import Caretaker
from models.patient import Patient
from models.medicine import Medicine
from models.schedule import Schedule
from models.tablet_image import TabletImage
from models.log import Log
