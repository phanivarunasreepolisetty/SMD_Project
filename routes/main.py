"""
Main Routes
Home page and common routes
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('caretaker.dashboard'))
    return render_template('index.html')


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
