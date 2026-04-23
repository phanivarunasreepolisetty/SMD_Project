"""
Decision Service
Compares AI prediction with scheduled medicine and determines action
"""
from config import Config


class DecisionService:
    """Service for processing verification decisions"""
    
    def __init__(self):
        """Initialize decision service"""
        self.confidence_threshold = Config.CONFIDENCE_THRESHOLD
    
    def process_decision(self, predicted_medicine, confidence, expected_medicine, is_match=None):
        """
        Process the verification decision
        """
        # Normalize medicine names for comparison
        predicted_lower = predicted_medicine.lower().strip()
        expected_lower = expected_medicine.lower().strip()
        
        # Check if names match (partial match allowed)
        names_match = (predicted_lower in expected_lower or 
                      expected_lower in predicted_lower or
                      self._fuzzy_match(predicted_lower, expected_lower))
        
        # If we have an explicit signal from the AI (is_match), it takes precedence.
        # AI models can confidently say "This is NOT a match" (is_match=False, confidence=0.99)
        if is_match is not None:
            names_match = is_match

        # If it's explicitly not a match, immediately return wrong
        if not names_match:
             return {
                'decision': 'wrong',
                'alert_text': f'Warning! Wrong medicine detected. Expected {expected_medicine}, but found {predicted_medicine}. Please check.',
                'action': 'block_intake',
                'confidence': confidence,
                'matched': False
            }

        # If it IS a match, ensure the confidence is high enough
        if confidence >= self.confidence_threshold:
            return {
                'decision': 'correct',
                'alert_text': f'Correct medicine verified: {expected_medicine}. You may take it now.',
                'action': 'allow_intake',
                'confidence': confidence,
                'matched': True
            }
        else:
            return {
                'decision': 'uncertain',
                'alert_text': 'Cannot clearly identify the tablet. Please hold it steady and try again.',
                'action': 'retry',
                'confidence': confidence,
                'matched': names_match if is_match is not None else None
            }
    
    def _fuzzy_match(self, str1, str2):
        """
        Simple fuzzy matching for medicine names
        
        Handles cases like:
        - "paracetamol" vs "paracetamol 500mg"
        - "aspirin" vs "aspirin tablet"
        """
        # Extract base name (first word)
        base1 = str1.split()[0] if str1 else ''
        base2 = str2.split()[0] if str2 else ''
        
        return base1 == base2
    
    def get_voice_alert(self, decision):
        """
        Get voice alert text based on decision
        
        Args:
            decision: Decision type ('correct', 'wrong', 'uncertain')
            
        Returns:
            String for voice synthesis
        """
        alerts = {
            'correct': 'Correct medicine verified. You may take your tablet now.',
            'wrong': 'Warning! This is the wrong medicine. Please do not take it and check again.',
            'uncertain': 'Unable to identify the tablet clearly. Please position it properly and try again.',
            'missed': 'Reminder: You have a pending medicine. Please take it now.',
            'overdue': 'Alert: Your scheduled medicine time has passed. Please take your medicine as soon as possible.'
        }
        
        return alerts.get(decision, 'Please consult your caretaker.')
    
    def get_decision_color(self, decision):
        """Get CSS color class for decision display"""
        colors = {
            'correct': 'success',
            'wrong': 'danger',
            'uncertain': 'warning'
        }
        return colors.get(decision, 'secondary')
