"""
AI-Based Smart Medicine Dispenser
Main Flask Application Entry Point
"""
import os


import os
from flask import Flask
from flask_login import LoginManager
from config import config, Config
from models import db




# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'caretaker.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    """Application factory function"""
    
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Create upload folders
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.TABLET_IMAGES_FOLDER, exist_ok=True)
    os.makedirs(Config.CAPTURED_IMAGES_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models.caretaker import Caretaker
        return Caretaker.query.get(int(user_id))
    
    # Register blueprints
    from routes.main import main_bp
    from routes.caretaker import caretaker_bp
    from routes.patient import patient_bp
    from routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(caretaker_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(api_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Context processor for templates
    @app.context_processor
    def inject_globals():
        from datetime import date, datetime
        return {
            'today': date.today(),
            'now': datetime.now()
        }
    
    return app


# Create the application instance
# Create the application instance
app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  AI-Based Smart Medicine Dispenser")
    print("  Starting Development Server (HTTPS Enabled)...")
    print("=" * 60)
    print()
    print("  Access the application at: https://127.0.0.1:5000")
    print()
    print("  Routes:")
    print("    - Home: https://127.0.0.1:5000/")
    print("    - Caretaker Login: https://127.0.0.1:5000/caretaker/login")
    print("    - Patient Login: https://127.0.0.1:5000/patient/login")
    print()
    print("=" * 60)
    # app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')  
    # app.run(host="0.0.0.0", port=5000, debug=True)
    
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
  