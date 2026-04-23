"""
AI Service
Image preprocessing and CNN prediction for tablet identification

This is a conceptual implementation that demonstrates the AI pipeline.
In a production system, this would use a properly trained CNN model.
"""
import os
import numpy as np
import requests
import ssl
import sys
import io
from config import Config
# from transformers import pipeline

# Bypass SSL for model downloads (EasyOCR needs this in some environments)
ssl._create_default_https_context = ssl._create_unverified_context

# Fix encoding for Windows terminals (helps with progress bars)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# try:
#     # from transformers import pipeline
#     class AIService:
#       def get_advice(self, medicine_name):
        
#         return f"Take {medicine_name} on time and follow doctor instructions."
#     from PIL import Image
#     # TRANSFORMERS_AVAILABLE = True
# except ImportError:
#     TRANSFORMERS_AVAILABLE = False


try:
    from PIL import Image
    TRANSFORMERS_AVAILABLE = False  # force disable
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class AIService:
    """AI service for tablet image verification"""
    
    def __init__(self):
        """Initialize the AI service"""
        self.image_size = Config.IMAGE_SIZE
        self.confidence_threshold = Config.CONFIDENCE_THRESHOLD
        
        # Config for chat and vision fallback
        self.groq_api_key = Config.GROQ_API_KEY
        self.model = Config.GROQ_MODEL
        
        # Models are lazy-loaded to save memory
        self.ocr_reader = None
        self.zs_pipeline = None

    def _get_ocr_reader(self):
        """Lazy load EasyOCR reader"""
        if self.ocr_reader is None and OCR_AVAILABLE:
            try:
                print("Initializing EasyOCR reader (CPU mode)...")
                self.ocr_reader = easyocr.Reader(['en'], gpu=False)
                print("EasyOCR initialized.")
            except Exception as e:
                print(f"Failed to initialize EasyOCR: {e}")
        return self.ocr_reader

    # def _get_zs_pipeline(self):
    #     """Lazy load Zero-Shot pipeline"""
    #     if self.zs_pipeline is None and TRANSFORMERS_AVAILABLE:
    #         try:
    #             print("Initializing local zero-shot image classification model (fallback)...")
    #             self.zs_pipeline = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")
    #             print("Zero-shot model initialized successfully.")
    #         except Exception as e:
    #             print(f"Failed to initialize zero-shot model: {e}")
    #     return self.zs_pipeline
    
    def _get_zs_pipeline(self):
     return None
    
    def preprocess_image(self, image_path):
        """
        Preprocess image for CNN prediction
        
        Steps:
        1. Load image using OpenCV
        2. Resize to 224x224 pixels
        3. Convert BGR to RGB
        4. Normalize pixel values to 0-1 range
        5. Expand dimensions for batch processing
        
        Args:
            image_path: Path to the tablet image
            
        Returns:
            Preprocessed numpy array ready for prediction
        """
        try:
            import cv2
            
            # Load image
            image = cv2.imread(image_path)
            
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Resize to model input size
            image = cv2.resize(image, self.image_size)
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Normalize to 0-1 range
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image
            
        except ImportError:
            print("OpenCV not installed. Using placeholder.")
            # Return dummy preprocessed image
            return np.zeros((1, 224, 224, 3), dtype=np.float32)
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    
    def _query_openfda(self, imprint_text):
        """Query the openFDA database for drug identification based on imprint"""
        if not imprint_text or len(imprint_text) < 2:
            return None
        
        import re
        # Try a few variations for searching
        search_terms = [f'"{imprint_text}"']
        
        # If it's like IP109, also try "IP 109" (handled by joining parts)
        parts = re.findall(r'[A-Z0-9]+', imprint_text)
        # More specific: split letters and numbers for "IP 109" style search
        parts = re.findall(r'[A-Z]+|[0-9]+', imprint_text)
        if len(parts) > 1:
            search_terms.append(f'"{ " ".join(parts) }"')
        
        for term in search_terms:
            try:
                # openFDA search is broad if we just use ?search="term"
                url = f"https://api.fda.gov/drug/label.json?search={term}&limit=1"
                print(f"Querying FDA with term: {term}")
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data and len(data['results']) > 0:
                        result = data['results'][0]
                        openfda = result.get('openfda', {})
                        
                        # Try to get brand name or generic name
                        medicine_name = None
                        if openfda.get('brand_name'):
                            medicine_name = openfda['brand_name'][0]
                        elif openfda.get('generic_name'):
                            medicine_name = openfda['generic_name'][0]
                        elif result.get('package_label_principal_display_panel'):
                            # package label often has the name
                            medicine_name = result['package_label_principal_display_panel'][0].split('\n')[0]
                            
                        if medicine_name:
                            print(f"Match found for {term}: {medicine_name}")
                            
                            # Extract advice content
                            warnings = result.get('warnings', ['No specific warnings listed.'])[0]
                            indications = result.get('indications_and_usage', ['Used as directed by your doctor.'])[0]
                            
                            # Clean up if they are long lists
                            if isinstance(warnings, list): warnings = warnings[0]
                            if isinstance(indications, list): indications = indications[0]
                            
                            return {
                                'medicine_name': medicine_name,
                                'imprint': term.strip('"'),
                                'warnings': warnings,
                                'indications': indications
                            }
            except Exception as e:
                print(f"OpenFDA query error for {term}: {e}")
        return None

    def predict_tablet(self, image_path, expected_medicine=None, reference_image_paths=None):
        """
        Predict tablet type using fast Groq Vision API
        """
        import base64
        import json
        
        if not self.groq_api_key:
            return self._run_demo_mode(expected_medicine)
            
        try:
            print(f"Running Groq Vision fast analysis for: {expected_medicine or 'Unknown'}")
            
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
            # Create content block with the captured image
            content = [
                {"type": "text", "text": f"Analyze this captured image of a tablet/pill."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_string}"
                    }
                }
            ]
            
            # Write debug logs to a file so we can view them reliably
            debug_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ai_debug.log')
            with open(debug_log_path, 'a') as f:
                f.write(f"\n--- NEW PREDICTION FOR {expected_medicine} ---\n")
                if reference_image_paths:
                    f.write(f"References found: {len(reference_image_paths)}\n")
                else:
                    f.write("NO reference images found!\n")
            
            # Add reference images if available
            has_reference = False
            if reference_image_paths and len(reference_image_paths) > 0:
                has_reference = True
                content.append({"type": "text", "text": f"\n\nHere is the REFERENCE image for what {expected_medicine or 'the medicine'} should actually look like. YOU MUST COMPARE THE CAPTURED IMAGE AGAINST THIS REFERENCE(S):"})
                # Limit to first 2 reference images to avoid payload size issues
                for ref_path in reference_image_paths[:2]:
                    try:
                        with open(ref_path, "rb") as ref_file:
                            ref_encoded = base64.b64encode(ref_file.read()).decode('utf-8')
                            content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{ref_encoded}"
                                }
                            })
                    except Exception as e:
                        with open(debug_log_path, 'a') as f:
                            f.write(f"Failed to load reference image {ref_path}: {e}\n")
            
            prompt_text = f"""
You are a strict pharmacist AI verifying a patient's medication.
The patient is supposed to take: {expected_medicine or 'an unknown medicine'}.

STRICT COMPARISON INSTRUCTIONS:
1. Examine the first image (captured by patient). Identify any text, imprints, shape, and color.
2. If reference images are provided (image 2+), examine them to understand exactly what {expected_medicine} looks like.
3. Compare the captured pill to the reference pill. If the color, shape, or text clearly do not match, it is NOT the right medicine.
4. If the captured pill has readable text that contradicts {expected_medicine}, it is NOT a match.
5. If the image is entirely blurry, empty, or you cannot see a pill, it is NOT a match.

You must output ONLY a valid JSON object with the following keys exactly:
- "observations": (string) Describe the pill in the captured image (color, shape, text).
- "comparison": (string) Compare it to the reference image or expected medicine.
- "is_match": (boolean) true ONLY if the captured pill is definitely the expected medicine. false otherwise.
- "medicine_name": (string) What you believe the captured medicine actually is (or "Unknown").
- "confidence": (float) A number between 0.0 and 1.0 indicating your certainty.
- "reason": (string) A short sentence explaining the final decision.
"""
            content[0]["text"] = prompt_text + "\n" + content[0]["text"]
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                response_content = result['choices'][0]['message']['content']
                
                with open(debug_log_path, 'a') as f:
                    f.write(f"Groq Response:\n{response_content}\n")
                try:
                    # Robust JSON parsing in case of markdown formatting
                    clean_content = response_content.strip()
                    if clean_content.startswith('```json'):
                        clean_content = clean_content[7:]
                    elif clean_content.startswith('```'):
                        clean_content = clean_content[3:]
                    if clean_content.endswith('```'):
                        clean_content = clean_content[:-3]
                    clean_content = clean_content.strip()
                    data = json.loads(clean_content)
                except json.JSONDecodeError as e:
                    with open(debug_log_path, 'a') as f:
                        f.write(f"JSON Parsing Error: {e} with content: {response_content}\n")
                    data = {}
                
                is_match_val = data.get('is_match', False)
                if isinstance(is_match_val, str):
                    is_match_val = is_match_val.lower() == 'true'
                else:
                    is_match_val = bool(is_match_val)
                    
                with open(debug_log_path, 'a') as f:
                    f.write(f"Parsed is_match: {is_match_val}\n")
                    f.write(f"Parsed medicine_name: {data.get('medicine_name', 'Unknown')}\n")
                
                return {
                    'medicine_name': data.get('medicine_name', 'Unknown'),
                    'confidence': float(data.get('confidence', 0.5)),
                    'success': True,
                    'message': data.get('reason', 'Analyzed by fast AI Vision'),
                    'is_match': is_match_val
                }
            else:
                with open(debug_log_path, 'a') as f:
                    f.write(f"Groq API error: {response.text}\n")
                return {
                    'medicine_name': 'Unknown',
                    'confidence': 0.0,
                    'success': False,
                    'message': f"API Error: {response.status_code}",
                    'is_match': False
                }
                
        except Exception as e:
            print(f"Vision API error: {e}")
            with open(debug_log_path, 'a') as f:
                f.write(f"Vision API exception: {e}\n")
            return {
                'medicine_name': 'Unknown',
                'confidence': 0.0,
                'success': False,
                'message': f"Connection Error: {e}",
                'is_match': False
            }

    def _run_demo_mode(self, expected_medicine):
        """Original demo simulation fallback"""
        import random
        demo_medicines = ['Paracetamol 500mg', 'Metformin 500mg', 'Aspirin 75mg', 'Vitamin D3']
        
        if expected_medicine and random.random() < 0.95: 
            predicted_medicine = expected_medicine
            confidence = random.uniform(0.86, 0.99)
        else:
            predicted_medicine = random.choice(demo_medicines)
            confidence = random.uniform(0.60, 0.80)
        
        return {
            'medicine_name': predicted_medicine,
            'confidence': round(confidence, 4),
            'success': True,
            'demo_mode': True,
            'message': 'Demo prediction (No reference images)'
        }
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            'ocr_available': OCR_AVAILABLE,
            'zero_shot_available': TRANSFORMERS_AVAILABLE,
            'image_size': self.image_size,
            'confidence_threshold': self.confidence_threshold
        }

    def get_chat_response(self, message, context=None):
        """
        Get a conversational response for a user message
        """
        if not self.groq_api_key:
            return "I'm sorry, my AI communication channel is not configured. Please provide a Groq API key in the configuration."
            
        system_prompt = f"""
        You are a helpful and knowledgeable AI Medical Assistant for the Smart Medicine Dispenser.
        Your goal is to help patients understand their medications, schedules, and general health safety.
        
        Guidelines:
        1. Always prioritize safety. If a question is about a medical emergency, advise the user to contact emergency services.
        2. Provide clear, concise information about medications.
        3. Use a friendly, reassuring tone.
        4. If context about the patient's schedule is provided, use it to give personalized advice.
        5. Do not prescribe new medications; only help manage existing ones.
        
        Patient Context: {context if context else 'No specific schedule info provided.'}
        """
        
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model, # Use the model from configuration
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"I'm having a bit of trouble connecting to my brain right now. Please try again later. (Error: {response.status_code})"
                
        except Exception as e:
            return f"I encountered an error while thinking: {str(e)}"


class ImagePreprocessor:
    """
    Utility class for image preprocessing operations
    
    This class provides static methods for various image operations
    used in the tablet verification pipeline.
    """
    
    @staticmethod
    def enhance_image(image):
        """
        Enhance image quality for better prediction
        
        Operations:
        - Adjust brightness and contrast
        - Apply slight blur to reduce noise
        - Sharpen edges
        """
        try:
            import cv2
            
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            return enhanced
        except:
            return image
    
    @staticmethod
    def detect_tablet_region(image):
        """
        Detect and crop the tablet region from image
        
        Uses edge detection and contour finding to locate
        the tablet in the image.
        """
        try:
            import cv2
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get largest contour (assumed to be the tablet)
                largest = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest)
                
                # Crop with padding
                padding = 10
                x = max(0, x - padding)
                y = max(0, y - padding)
                cropped = image[y:y+h+2*padding, x:x+w+2*padding]
                
                return cropped
            
            return image
        except:
            return image
