"""
API Routes
REST endpoints for camera capture, AI verification, and decision processing
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import os
import base64
import uuid
from models import db
from models.patient import Patient
from models.medicine import Medicine
from models.schedule import Schedule
from models.log import Log
from services.ai_service import AIService
from services.decision_service import DecisionService
from config import Config

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize services
ai_service = AIService()
decision_service = DecisionService()


@api_bp.route('/capture-image', methods=['POST'])
def capture_image():
    """Receive and save captured tablet image"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
        
        schedule_id = data.get('schedule_id')
        image_data = data.get('image')  # base64 encoded image
        
        # Decode and save image
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        # Create captures folder if needed
        captures_folder = Config.CAPTURED_IMAGES_FOLDER
        os.makedirs(captures_folder, exist_ok=True)
        
        # Generate unique filename
        filename = f'capture_{schedule_id}_{uuid.uuid4().hex[:8]}.jpg'
        filepath = os.path.join(captures_folder, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        relative_path = os.path.join('captures', filename)
        
        return jsonify({
            'success': True,
            'image_path': relative_path,
            'message': 'Image captured successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/verify-tablet', methods=['POST'])
def verify_tablet():
    """Verify captured tablet using AI model"""
    try:
        data = request.get_json()
        
        image_path = data.get('image_path')
        schedule_id = data.get('schedule_id')
        
        if not image_path or not schedule_id:
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Get full path
        full_path = os.path.join(Config.UPLOAD_FOLDER, image_path)
        
        # Get schedule info first
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'success': False, 'error': 'Schedule not found'}), 404
        
        expected_medicine = schedule.medicine.name
        
        # Get reference image paths
        reference_image_paths = [img.get_full_path() for img in schedule.medicine.images]
        
        if not reference_image_paths:
             # If no reference images, we might want to log this or handle it in ai_service
             print(f"Warning: No reference images for {expected_medicine}")

        # Run AI prediction with context
        prediction = ai_service.predict_tablet(
            full_path, 
            expected_medicine=expected_medicine,
            reference_image_paths=reference_image_paths
        )
        
        if not prediction.get('success', False):
            # API failure should be uncertain, not a definitive wrong medicine
            decision = {
                'decision': 'uncertain',
                'alert_text': f"AI Verification failed: {prediction.get('message', 'Unknown error')}",
                'action': 'retry',
                'confidence': 0.0,
                'matched': None
            }
        else:
            # Process decision
            decision = decision_service.process_decision(
                predicted_medicine=prediction['medicine_name'],
                confidence=prediction['confidence'],
                expected_medicine=expected_medicine,
                is_match=prediction.get('is_match')
            )
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'decision': decision
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/process-decision', methods=['POST'])
def process_decision():
    """Process the final decision and update records"""
    try:
        data = request.get_json()
        
        schedule_id = data.get('schedule_id')
        decision = data.get('decision')  # 'correct', 'wrong', 'uncertain'
        predicted_medicine = data.get('predicted_medicine')
        confidence = data.get('confidence')
        image_path = data.get('image_path')
        
        # Get patient from session
        patient_id = session.get('patient_id')
        if not patient_id:
            return jsonify({'success': False, 'error': 'Patient not logged in'}), 401
        
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'success': False, 'error': 'Schedule not found'}), 404
        
        # Update schedule based on decision
        if decision == 'correct':
            schedule.mark_as_taken()
            status = 'taken'
            message = 'Correct medicine verified. You may take it now.'
            alert_type = 'success'
        elif decision == 'wrong':
            # Do NOT finalize status, allow retry
            status = 'wrong_attempt'
            message = 'Warning! This is the wrong medicine. Please check again.'
            alert_type = 'danger'
        else:
            status = 'pending'
            message = 'Cannot clearly identify the tablet. Please try again.'
            alert_type = 'warning'
        
        # Create log entry
        log = Log.create_intake_log(
            patient_id=patient_id,
            medicine_id=schedule.medicine_id,
            schedule_id=schedule_id,
            status=status,
            predicted_medicine=predicted_medicine,
            confidence=confidence,
            image_path=image_path
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'status': status,
            'message': message,
            'alert_type': alert_type
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/get-pending-schedules', methods=['GET'])
def get_pending_schedules():
    """Get pending schedules for current patient"""
    try:
        patient_id = session.get('patient_id')
        if not patient_id:
            return jsonify({'success': False, 'error': 'Patient not logged in'}), 401
        
        from datetime import date
        schedules = Schedule.query.filter_by(
            patient_id=patient_id,
            scheduled_date=date.today(),
            status='pending'
        ).order_by(Schedule.scheduled_time).all()
        
        schedule_data = []
        for s in schedules:
            schedule_data.append({
                'id': s.id,
                'medicine_name': s.medicine.name,
                'dosage': s.medicine.dosage,
                'time': s.get_time_display(),
                'time_slot': s.time_slot
            })
        
        return jsonify({
            'success': True,
            'schedules': schedule_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/mark-missed', methods=['POST'])
def mark_missed():
    """Mark a schedule as missed"""
    try:
        data = request.get_json()
        schedule_id = data.get('schedule_id')
        
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'success': False, 'error': 'Schedule not found'}), 404
        
        schedule.mark_as_missed()
        
        # Create log
        log = Log.create_intake_log(
            patient_id=schedule.patient_id,
            medicine_id=schedule.medicine_id,
            schedule_id=schedule_id,
            status='missed'
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Marked as missed'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@api_bp.route('/get-medication-advice/<int:schedule_id>', methods=['GET'])
def get_medication_advice(schedule_id):
    """Get conversational advice for a medication from OpenFDA"""
    try:
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return jsonify({'success': False, 'error': 'Schedule not found'}), 404
            
        medicine = schedule.medicine
        
        # Use AI service to query FDA for this medicine's details
        # We use a broad search by name
        info = ai_service._query_openfda(medicine.name)
        
        if info:
            advice = {
                'name': info['medicine_name'],
                'indications': info.get('indications', 'Used as directed by your doctor.'),
                'warnings': info.get('warnings', 'No specific warnings listed.'),
                'summary': f"This medication, {medicine.name}, is typically {info.get('indications', 'used as directed')}. Important: {info.get('warnings', 'Please follow standard precautions.')}"
            }
        else:
            advice = {
                'name': medicine.name,
                'indications': 'Take as prescribed by your doctor.',
                'warnings': 'Follow standard safety precautions.',
                'summary': f"Take {medicine.name} as prescribed. {medicine.instructions or 'Follow the dosage on the label.'}"
            }
            
        return jsonify({
            'success': True,
            'advice': advice
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@api_bp.route('/check-triggers', methods=['GET'])
def check_triggers():
    """Check for new medication triggers in real-time"""
    try:
        patient_id = session.get('patient_id')
        if not patient_id:
            return jsonify({'success': False, 'error': 'Patient not logged in'}), 401
            
        from datetime import date, time
        now = datetime.now().time()
        
        # Find pending schedules for today
        schedules = Schedule.query.filter_by(
            patient_id=patient_id,
            scheduled_date=date.today(),
            status='pending'
        ).all()
        
        triggers = []
        for s in schedules:
            # Check if scheduled time has arrived or passed (within last 30 mins)
            # This allows the AI to catch missed doses but focus on "just became due"
            s_time = s.scheduled_time
            
            # Simple time comparison: if s_time <= now
            if s_time <= now:
                # Calculate how long ago it was
                diff_minutes = (datetime.combine(date.today(), now) - datetime.combine(date.today(), s_time)).total_seconds() / 60
                
                if diff_minutes < 30: # Only trigger if reasonably recent
                    triggers.append({
                        'id': s.id,
                        'name': s.medicine.name,
                        'dosage': s.medicine.dosage,
                        'time': s.get_time_display(),
                        'time_slot': s.time_slot,
                        'urgency': 'high' if diff_minutes < 5 else 'medium'
                    })
        
        return jsonify({
            'success': True,
            'triggers': triggers
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/chat', methods=['POST'])
def chat():
    """Handle AI consultation chat messages"""
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
            
        patient_id = session.get('patient_id')
        context = ""
        
        if patient_id:
            from datetime import date
            schedules = Schedule.query.filter_by(
                patient_id=patient_id,
                scheduled_date=date.today()
            ).all()
            
            if schedules:
                context = "Patient's Today Schedule: " + ", ".join([
                    f"{s.medicine.name} ({s.time_slot} - {s.status})" for s in schedules
                ])
        
        response_text = ai_service.get_chat_response(message, context=context)
        
        return jsonify({
            'success': True,
            'response': response_text
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
