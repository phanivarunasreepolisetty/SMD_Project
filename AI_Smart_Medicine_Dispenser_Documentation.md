# AI-Based Smart Medicine Dispenser System
## Final Year Project Documentation

---

# 1. Project Overview

## 1.1 Problem Statement

Medication non-adherence is a critical healthcare challenge affecting millions of patients worldwide. Elderly patients, chronic disease sufferers, and individuals with cognitive impairments often face difficulties in:

- Remembering correct medication timings
- Identifying the right tablet from multiple prescriptions
- Tracking missed doses
- Maintaining accurate medication logs

Traditional pill boxes and manual reminders are prone to human error and do not provide verification of whether the correct medicine was consumed.

## 1.2 Motivation

The need for a smart, automated, and verified medicine dispensing system arises from:

- **Patient Safety**: Wrong medication intake can cause serious health complications
- **Caretaker Burden**: Family members and healthcare providers struggle to monitor medication compliance remotely
- **Healthcare Costs**: Medication errors lead to hospitalizations and increased medical expenses
- **Aging Population**: Growing elderly population requires accessible healthcare solutions

## 1.3 Proposed Solution

The **AI-Based Smart Medicine Dispenser** is a web-based application that:

- Allows caretakers to register patients and schedule medications
- Uses a camera to capture images of tablets before consumption
- Employs AI-based image recognition to verify if the correct tablet is being taken
- Provides voice alerts for correct/wrong tablet detection
- Logs all medication activities for monitoring and reporting
- Offers a dashboard for caretakers to track patient compliance

This system bridges the gap between manual medication management and intelligent healthcare assistance.

---

# 2. System Architecture

## 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI-BASED SMART MEDICINE DISPENSER                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │   CARETAKER      │    │    PATIENT       │    │   VERIFICATION   │   │
│  │   INTERFACE      │    │   INTERFACE      │    │     MODULE       │   │
│  │                  │    │                  │    │                  │   │
│  │ - Patient Reg.   │    │ - View Schedule  │    │ - Image Capture  │   │
│  │ - Medicine Mgmt  │    │ - Take Medicine  │    │ - AI Analysis    │   │
│  │ - Dataset Upload │    │ - Voice Alerts   │    │ - CNN Processing │   │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘   │
│           │                       │                       │              │
│           └───────────────────────┼───────────────────────┘              │
│                                   │                                      │
│                          ┌────────▼────────┐                            │
│                          │  FLASK BACKEND  │                            │
│                          │   (Python)      │                            │
│                          └────────┬────────┘                            │
│                                   │                                      │
│           ┌───────────────────────┼───────────────────────┐              │
│           │                       │                       │              │
│  ┌────────▼─────────┐    ┌────────▼────────┐    ┌────────▼─────────┐   │
│  │   DECISION       │    │    LOGGING &    │    │   CARETAKER      │   │
│  │   MODULE         │    │   MONITORING    │    │   DASHBOARD      │   │
│  │                  │    │                 │    │                  │   │
│  │ - Correct/Wrong  │    │ - Intake Logs   │    │ - Reports        │   │
│  │ - Alert Trigger  │    │ - Missed Doses  │    │ - Analytics      │   │
│  └──────────────────┘    └────────┬────────┘    └──────────────────┘   │
│                                   │                                      │
│                          ┌────────▼────────┐                            │
│                          │  SQLite DATABASE│                            │
│                          │  (Data Storage) │                            │
│                          └─────────────────┘                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Module Descriptions

### 2.2.1 Caretaker Interface

**Purpose**: Allows caretakers (family members, nurses, or healthcare providers) to manage patient information and medication schedules.

**Key Functions**:
- Register new patients with personal and medical details
- Add medicines with dosage, timing, and frequency
- Upload tablet images for the AI training dataset
- View and edit existing patient records

**Implementation**:
- HTML forms rendered via Jinja2 templates
- Flask routes handle form submissions
- Data stored in SQLite database

---

### 2.2.2 Patient Interface

**Purpose**: Provides a simple interface for patients to view their medication schedule and initiate the verification process.

**Key Functions**:
- Display current medication schedule
- Show pending medicines for the day
- Initiate camera capture for tablet verification
- Receive voice confirmation/alerts

**Implementation**:
- Minimal, easy-to-read interface
- Large buttons for elderly accessibility
- JavaScript for camera interaction

---

### 2.2.3 AI Verification Module

**Purpose**: Uses computer vision and machine learning to identify and verify tablets from camera images.

**Key Functions**:
- Capture tablet image using device camera
- Preprocess image (resize, normalize, enhance)
- Pass image through trained CNN model
- Return prediction with confidence score

**Conceptual Working**:
1. **Image Capture**: JavaScript accesses device camera via WebRTC API
2. **Preprocessing**: OpenCV resizes image to 224x224 pixels, converts to grayscale, applies normalization
3. **Feature Extraction**: CNN extracts features like shape, color, markings
4. **Classification**: Model predicts tablet class from trained dataset
5. **Confidence Check**: If confidence > threshold (e.g., 85%), tablet is identified

---

### 2.2.4 Decision Module

**Purpose**: Compares the AI prediction with the scheduled medicine and triggers appropriate alerts.

**Key Functions**:
- Match predicted tablet with scheduled medicine
- Determine outcome: Correct, Wrong, or Unknown
- Trigger voice alerts based on outcome
- Log the decision for records

**Decision Logic**:
```
IF predicted_tablet == scheduled_tablet AND confidence >= 85%:
    Result = "CORRECT"
    Alert = "Correct medicine. You may take it."
    
ELSE IF predicted_tablet != scheduled_tablet:
    Result = "WRONG"
    Alert = "Warning! Wrong medicine detected. Please check."
    
ELSE:
    Result = "UNKNOWN"
    Alert = "Unable to identify. Please show clearly."
```

---

### 2.2.5 Logging & Monitoring Module

**Purpose**: Records all medication-related activities for compliance tracking and analysis.

**Key Functions**:
- Log successful medicine intakes
- Record missed doses with timestamps
- Track wrong tablet attempts
- Generate activity history

**Data Logged**:
- Patient ID
- Medicine name
- Scheduled time
- Actual intake time
- Status (Taken, Missed, Wrong Attempt)

---

### 2.2.6 Caretaker Dashboard

**Purpose**: Provides real-time monitoring and reporting capabilities for caretakers.

**Key Functions**:
- View patient compliance statistics
- Check today's pending medicines
- Review logs and history
- Generate reports (daily, weekly, monthly)
- Receive alerts for missed doses

---

# 3. Technology Stack Used

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Frontend** | HTML5, CSS3, JavaScript | Standard web technologies; accessible on all devices; no complex framework needed for academic project |
| **Templating** | Jinja2 | Native Flask integration; easy to render dynamic content; simple syntax |
| **Backend** | Python, Flask | Lightweight framework; easy to learn; extensive library support for AI/ML |
| **Database** | SQLite with Flask-SQLAlchemy | File-based database; no server setup required; suitable for prototype; ORM simplifies queries |
| **Image Processing** | OpenCV | Industry-standard library; handles image preprocessing; works well with Python |
| **AI/ML** | CNN (Convolutional Neural Network) | Best for image classification tasks; can identify visual patterns in tablets |
| **Voice Alerts** | Web Speech API (JavaScript) | Browser-native; no external dependencies; works offline |
| **Development** | VS Code | Free, powerful IDE; excellent Python and Flask extensions |
| **Testing** | Google Chrome | Developer tools for debugging; good camera API support |

## 3.1 Why Flask?

- **Simplicity**: Minimal boilerplate code compared to Django
- **Flexibility**: No forced project structure
- **Learning Curve**: Easy for students to understand and implement
- **Integration**: Works seamlessly with Python ML libraries
- **Academic Suitability**: Sufficient for prototype-level projects

## 3.2 Why SQLite?

- **Zero Configuration**: No database server installation
- **Portability**: Single file, easy to backup and transfer
- **Sufficient Performance**: Handles prototype-level data efficiently
- **SQLAlchemy ORM**: Abstracts raw SQL, provides Pythonic interface

## 3.3 Why OpenCV + CNN?

- **OpenCV**: Handles image loading, resizing, color conversion, and preprocessing
- **CNN**: Specialized for image recognition; learns hierarchical features; proven accuracy for image classification

---

# 4. Database Design

## 4.1 Entity-Relationship Overview

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  CARETAKER  │──────<│   PATIENT   │──────<│  MEDICINE   │
└─────────────┘       └─────────────┘       └─────────────┘
                             │                     │
                             │                     │
                      ┌──────▼──────┐       ┌──────▼──────┐
                      │  SCHEDULE   │       │   TABLET    │
                      │   (Daily)   │       │   IMAGE     │
                      └──────┬──────┘       └─────────────┘
                             │
                      ┌──────▼──────┐
                      │    LOG      │
                      │  (History)  │
                      └─────────────┘
```

## 4.2 Table Descriptions

### Table 1: Caretaker

| Attribute | Type | Purpose |
|-----------|------|---------|
| caretaker_id | Integer (PK) | Unique identifier for caretaker |
| name | String | Full name of caretaker |
| email | String | Login email |
| password_hash | String | Encrypted password |
| phone | String | Contact number |
| created_at | DateTime | Registration timestamp |

**Purpose**: Stores caretaker accounts who manage patients.

---

### Table 2: Patient

| Attribute | Type | Purpose |
|-----------|------|---------|
| patient_id | Integer (PK) | Unique identifier for patient |
| caretaker_id | Integer (FK) | Links to managing caretaker |
| name | String | Patient's full name |
| age | Integer | Patient's age |
| gender | String | Gender (M/F/Other) |
| medical_conditions | Text | List of health conditions |
| created_at | DateTime | Registration timestamp |

**Purpose**: Stores patient personal and medical information.

---

### Table 3: Medicine

| Attribute | Type | Purpose |
|-----------|------|---------|
| medicine_id | Integer (PK) | Unique identifier for medicine |
| patient_id | Integer (FK) | Links to patient |
| name | String | Medicine/tablet name |
| dosage | String | Dosage (e.g., "500mg") |
| frequency | String | How often (e.g., "Twice daily") |
| instructions | Text | Special instructions |
| is_active | Boolean | Whether prescription is current |

**Purpose**: Stores medicine prescriptions for each patient.

---

### Table 4: Schedule

| Attribute | Type | Purpose |
|-----------|------|---------|
| schedule_id | Integer (PK) | Unique identifier |
| medicine_id | Integer (FK) | Links to medicine |
| patient_id | Integer (FK) | Links to patient |
| scheduled_time | Time | When to take medicine |
| scheduled_date | Date | Which date |
| status | String | Pending/Taken/Missed |

**Purpose**: Tracks daily medicine schedule and completion status.

---

### Table 5: TabletImage

| Attribute | Type | Purpose |
|-----------|------|---------|
| image_id | Integer (PK) | Unique identifier |
| medicine_id | Integer (FK) | Links to medicine type |
| image_path | String | Local file path to image |
| uploaded_at | DateTime | Upload timestamp |
| is_training | Boolean | Whether used for AI training |

**Purpose**: Stores tablet images for AI model training dataset.

---

### Table 6: Log

| Attribute | Type | Purpose |
|-----------|------|---------|
| log_id | Integer (PK) | Unique identifier |
| patient_id | Integer (FK) | Links to patient |
| medicine_id | Integer (FK) | Links to medicine |
| scheduled_time | DateTime | Original scheduled time |
| action_time | DateTime | Actual action time |
| status | String | Taken/Missed/Wrong Attempt |
| confidence_score | Float | AI prediction confidence |
| image_path | String | Path to captured image |
| notes | Text | Any additional notes |

**Purpose**: Complete history of all medication activities.

---

# 5. Detailed Module Description

## 5.1 Patient Registration Module

### Internal Working:

1. Caretaker navigates to `/caretaker/add-patient` route
2. Jinja2 template renders registration form
3. Caretaker fills patient details (name, age, gender, conditions)
4. Form submits via POST to Flask route
5. Flask validates input data
6. New Patient record created in database
7. Success message displayed
8. Redirects to patient list page

### Flask Route Mapping:

```
URL: /caretaker/add-patient
Method: GET → Renders form template
Method: POST → Processes form, saves to database
Template: templates/caretaker/add_patient.html
Database Table: Patient
```

---

## 5.2 Medicine Scheduling Module

### Internal Working:

1. Caretaker selects patient from list
2. Navigates to `/caretaker/patient/<id>/add-medicine`
3. Fills medicine details: name, dosage, timing
4. Specifies schedule: morning, afternoon, evening, night
5. Form submission triggers Flask route
6. Medicine record created
7. Daily Schedule entries auto-generated

### Schedule Generation Logic:

```
For each timing selected:
    Create Schedule entry with:
        - medicine_id
        - patient_id
        - scheduled_time (based on timing slot)
        - scheduled_date (current date onwards)
        - status = "Pending"
```

### Flask Route Mapping:

```
URL: /caretaker/patient/<id>/add-medicine
Methods: GET, POST
Template: templates/caretaker/add_medicine.html
Database Tables: Medicine, Schedule
```

---

## 5.3 Tablet Image Dataset Module

### Internal Working:

1. Caretaker navigates to `/caretaker/medicine/<id>/upload-image`
2. Interface shows file upload option
3. Caretaker captures/selects clear tablet image
4. Image uploaded via multipart form
5. Flask saves image to `uploads/tablets/<medicine_id>/` directory
6. File path stored in TabletImage table
7. Image appears in dataset gallery

### Image Storage Structure:

```
uploads/
└── tablets/
    ├── medicine_1/
    │   ├── img_001.jpg
    │   ├── img_002.jpg
    │   └── img_003.jpg
    └── medicine_2/
        ├── img_001.jpg
        └── img_002.jpg
```

### Flask Route Mapping:

```
URL: /caretaker/medicine/<id>/upload-image
Methods: GET, POST
Template: templates/caretaker/upload_image.html
Database Table: TabletImage
File Storage: uploads/tablets/
```

---

## 5.4 Camera Capture Module

### Internal Working:

1. Patient navigates to `/patient/take-medicine` route
2. Pending medicines for current time displayed
3. Patient clicks "Verify Tablet" button
4. JavaScript activates device camera via WebRTC
5. Live camera feed shown on screen
6. Patient positions tablet in frame
7. Clicks "Capture" button
8. Image captured as base64 data
9. Image sent to Flask backend via AJAX POST
10. Backend saves image temporarily for processing

### JavaScript Camera Integration:

```
navigator.mediaDevices.getUserMedia({ video: true })
    → Requests camera access
    → Displays live stream in <video> element
    → On capture: draws frame to <canvas>
    → Converts to base64 and sends to server
```

### Flask Route Mapping:

```
URL: /patient/take-medicine
Method: GET → Shows pending medicines
URL: /api/capture-image
Method: POST → Receives and saves captured image
```

---

## 5.5 AI Verification Module

### Internal Working (Conceptual):

1. Captured image received by Flask backend
2. Image loaded using OpenCV
3. **Preprocessing Steps**:
   - Resize to 224x224 pixels
   - Convert to RGB format
   - Normalize pixel values (0-1 range)
   - Apply slight blur to reduce noise
4. Preprocessed image passed to CNN model
5. **CNN Processing**:
   - Image passes through convolutional layers
   - Features extracted (edges, shapes, colors)
   - Pooling layers reduce dimensions
   - Fully connected layer produces class probabilities
6. Model returns:
   - Predicted medicine class
   - Confidence score (0-100%)

### CNN Architecture (Simplified):

```
Input Image (224x224x3)
    ↓
Conv Layer 1 (32 filters) + ReLU + MaxPool
    ↓
Conv Layer 2 (64 filters) + ReLU + MaxPool
    ↓
Conv Layer 3 (128 filters) + ReLU + MaxPool
    ↓
Flatten
    ↓
Dense Layer (256 units) + ReLU + Dropout
    ↓
Output Layer (N medicine classes) + Softmax
    ↓
Prediction: Medicine Name + Confidence %
```

### Flask Route Mapping:

```
URL: /api/verify-tablet
Method: POST
Input: Image file
Output: JSON {predicted_medicine, confidence, match_status}
```

---

## 5.6 Decision Module

### Internal Working:

1. Receives AI prediction results
2. Fetches scheduled medicine for current time slot
3. Compares predicted medicine with scheduled medicine
4. Determines result based on logic:

### Decision Matrix:

| Condition | Result | Action |
|-----------|--------|--------|
| Predicted = Scheduled AND Confidence ≥ 85% | CORRECT | Allow intake, play success voice |
| Predicted ≠ Scheduled | WRONG | Block intake, play warning voice |
| Confidence < 85% | UNCERTAIN | Request re-capture |
| No prediction possible | ERROR | Show error message |

5. Triggers appropriate voice alert
6. Updates Schedule status
7. Creates Log entry

### Flask Route:

```
URL: /api/process-decision
Method: POST
Input: prediction_result, schedule_id
Output: JSON {decision, voice_alert_text, log_id}
```

---

## 5.7 Voice Alert Module

### Internal Working:

1. Decision module returns alert text
2. JavaScript receives response
3. Web Speech API synthesizes speech:

```javascript
let utterance = new SpeechSynthesisUtterance(alertText);
utterance.lang = 'en-US';
utterance.rate = 0.9;  // Slightly slower for clarity
speechSynthesis.speak(utterance);
```

### Alert Messages:

| Status | Voice Message |
|--------|---------------|
| CORRECT | "Correct medicine verified. You may take your tablet now." |
| WRONG | "Warning! This is the wrong medicine. Please check and try again." |
| UNCERTAIN | "Cannot clearly identify the tablet. Please hold it steady and try again." |
| MISSED | "Reminder: You have a pending medicine. Please take it now." |

---

## 5.8 Logging Module

### Internal Working:

1. Every verification attempt triggers logging
2. Log entry created with:
   - Patient and medicine references
   - Scheduled vs actual time
   - Verification status
   - AI confidence score
   - Captured image path
3. Logs stored in database
4. Accessible via caretaker dashboard

### Log Statuses:

- **TAKEN**: Medicine correctly verified and consumed
- **MISSED**: Scheduled time passed without intake
- **WRONG_ATTEMPT**: Wrong tablet presented
- **PENDING**: Awaiting intake

---

## 5.9 Caretaker Dashboard Module

### Internal Working:

1. Caretaker logs in at `/caretaker/login`
2. Dashboard loads at `/caretaker/dashboard`
3. Dashboard queries database for:
   - Today's schedule status for all patients
   - Recent logs (last 24 hours)
   - Compliance statistics
   - Alerts for missed doses
4. Data rendered via Jinja2 template
5. Charts generated using JavaScript (Chart.js)

### Dashboard Components:

| Component | Data Displayed |
|-----------|----------------|
| Patient Cards | Name, pending today, compliance % |
| Today's Schedule | All medicines due today with status |
| Recent Activity | Last 10 intake/missed events |
| Alerts Section | Missed doses, wrong attempts |
| Statistics | Weekly compliance chart |

### Flask Route Mapping:

```
URL: /caretaker/dashboard
Method: GET
Template: templates/caretaker/dashboard.html
Data Sources: Patient, Schedule, Log tables
```

---

## 5.10 Reports Module

### Internal Working:

1. Caretaker selects patient and date range
2. Navigates to `/caretaker/reports`
3. Selects report type: Daily, Weekly, Monthly
4. Flask queries Log table with filters
5. Aggregates data:
   - Total scheduled doses
   - Taken count
   - Missed count
   - Wrong attempt count
   - Compliance percentage
6. Renders report table/chart
7. Option to download as PDF

### Report Metrics:

```
Compliance Rate = (Taken / Total Scheduled) × 100%
Miss Rate = (Missed / Total Scheduled) × 100%
Accuracy = (Correct Attempts / Total Attempts) × 100%
```

---

# 6. System Workflow

## Step-by-Step Flow

### Phase 1: Setup (Caretaker)

```
Step 1: Caretaker creates account
        └─→ Registers with email and password
        └─→ Account stored in Caretaker table

Step 2: Caretaker adds new patient
        └─→ Enters patient details
        └─→ Patient record created

Step 3: Caretaker adds medicines
        └─→ Selects patient
        └─→ Enters medicine name, dosage, timing
        └─→ Medicine and Schedule records created

Step 4: Caretaker uploads tablet images
        └─→ Captures clear images of each tablet
        └─→ Minimum 5-10 images per tablet type
        └─→ Images stored in dataset folder
```

### Phase 2: Daily Usage (Patient)

```
Step 5: Patient logs in
        └─→ Simple PIN or face-based login
        └─→ Dashboard shows today's schedule

Step 6: Medicine reminder triggers
        └─→ At scheduled time, alert appears
        └─→ Voice reminder plays

Step 7: Patient initiates verification
        └─→ Clicks "Take Medicine" button
        └─→ Camera interface opens

Step 8: Patient captures tablet image
        └─→ Positions tablet in camera view
        └─→ Clicks capture button
        └─→ Image sent to server

Step 9: AI processes image
        └─→ Image preprocessed
        └─→ CNN model predicts tablet type
        └─→ Confidence score calculated

Step 10: Decision module evaluates
         └─→ Compares prediction with schedule
         └─→ Determines correct/wrong/uncertain

Step 11: Voice alert plays
         └─→ Correct: "You may take your medicine"
         └─→ Wrong: "Warning! Wrong medicine"

Step 12: Log entry created
         └─→ Status, time, confidence recorded
         └─→ Schedule marked as taken/attempted
```

### Phase 3: Monitoring (Caretaker)

```
Step 13: Caretaker checks dashboard
         └─→ Views all patients' status
         └─→ Sees pending and completed medicines

Step 14: Caretaker reviews alerts
         └─→ Missed dose notifications
         └─→ Wrong attempt warnings

Step 15: Caretaker generates reports
         └─→ Selects patient and date range
         └─→ Views compliance statistics
         └─→ Downloads report if needed
```

---

# 7. Advantages of the System

## 7.1 Patient Safety

- **Medication Verification**: AI ensures correct tablet before intake
- **Wrong Medicine Prevention**: Real-time alerts prevent accidental consumption
- **Dosage Tracking**: No overdose through double intake

## 7.2 Simplicity

- **Easy Interface**: Large buttons, minimal navigation for elderly users
- **Voice Assistance**: Audio guidance reduces screen dependency
- **No Complex Hardware**: Uses standard smartphone/tablet camera

## 7.3 Medical Reliability

- **AI-Backed Accuracy**: Trained model provides consistent identification
- **Complete Logging**: Every action recorded for medical review
- **Caretaker Oversight**: Remote monitoring enables timely intervention

## 7.4 Accessibility

- **Web-Based**: Works on any device with browser and camera
- **Offline Capability**: Core features work without internet (future scope)
- **Multi-Language Support**: Voice alerts can be configured for local languages

## 7.5 Cost-Effectiveness

- **No Expensive Hardware**: Utilizes existing devices
- **Open Source Stack**: No licensing costs
- **Low Maintenance**: Simple SQLite database, minimal server requirements

## 7.6 Caretaker Benefits

- **Remote Monitoring**: Track patient compliance from anywhere
- **Instant Alerts**: Immediate notification of missed doses
- **Data-Driven Insights**: Reports help doctors adjust treatments

---

# 8. Use Cases

## 8.1 Elderly Care at Home

**Scenario**: Mr. Ramesh, 72 years old, lives alone and takes 5 different medicines daily.

**Problem**: He often confuses tablets that look similar and sometimes forgets doses.

**Solution**:
- Son registers him as patient via caretaker interface
- All medicines scheduled with images uploaded
- Mr. Ramesh uses the system to verify each tablet
- Son monitors compliance remotely via dashboard
- Voice alerts in native language help Mr. Ramesh

**Outcome**: Reduced medication errors, improved compliance, peace of mind for family.

---

## 8.2 Hospital Ward Management

**Scenario**: Hospital ward with 20 patients, each with different prescriptions.

**Problem**: Nurses must verify medicines manually; risk of mix-ups during shift changes.

**Solution**:
- Each patient registered with bed number
- Medicines scheduled according to doctor's orders
- Nurses use tablet camera to verify before administration
- AI confirms correct medicine for correct patient
- All administrations logged automatically

**Outcome**: Reduced human error, complete audit trail, improved patient safety.

---

## 8.3 Chronic Disease Management

**Scenario**: Mrs. Priya has diabetes and hypertension; takes medicines twice daily.

**Problem**: She travels frequently and misses evening doses; doctor needs compliance data.

**Solution**:
- System tracks scheduled vs actual intake times
- Reminders trigger even when traveling
- Monthly reports show compliance patterns
- Doctor adjusts treatment based on data

**Outcome**: Better disease management, data-driven treatment adjustments.

---

## 8.4 Post-Surgery Recovery

**Scenario**: Patient discharged after surgery with antibiotics and painkillers.

**Problem**: Must complete antibiotic course; painkillers should not be overused.

**Solution**:
- Critical medicines marked with high priority
- System prevents painkiller overdose by tracking frequency
- Alerts if antibiotic dose missed
- Recovery progress visible to doctor

**Outcome**: Complete antibiotic course, controlled painkiller usage.

---

## 8.5 Mental Health Medication

**Scenario**: Patient with depression requires daily medication at specific times.

**Problem**: Mood fluctuations may cause patient to skip or double doses.

**Solution**:
- Gentle voice reminders at scheduled times
- Family member set as caretaker for monitoring
- System logs patterns that indicate mood changes
- Psychiatrist reviews compliance data

**Outcome**: Consistent medication, early intervention possible.

---

# 9. Limitations

## 9.1 Academic-Level Constraints

1. **Limited AI Accuracy**: CNN model trained on small dataset may not generalize to all tablet variations

2. **Single Camera Angle**: System requires specific lighting and positioning; not robust to environmental variations

3. **No Hardware Integration**: Does not control physical dispenser; only verification system

4. **Internet Dependency**: Real-time monitoring requires connectivity

5. **Training Data Requirement**: New medicines require manual image collection and model retraining

## 9.2 Technical Limitations

1. **Browser Compatibility**: Camera access may vary across browsers and devices

2. **Database Scalability**: SQLite suitable for prototype; production needs PostgreSQL/MySQL

3. **Security**: Basic authentication; missing advanced security features

4. **Tablet Similarity**: Tablets of same color/shape may confuse model

## 9.3 Practical Limitations

1. **User Training**: Elderly users may need initial guidance

2. **Lighting Conditions**: Poor lighting affects image quality

3. **Multiple Tablets**: Cannot verify multiple tablets in single image

4. **Generic Medicines**: Different manufacturers' tablets may look different

## 9.4 Deployment Limitations

1. **Single Machine**: Current architecture runs on single server

2. **No Mobile App**: Web-only interface; no native app

3. **No Cloud Backup**: Data stored locally only

---

# 10. Future Enhancements

## 10.1 Short-Term (6-12 months)

1. **Transfer Learning**: Use pre-trained models (MobileNet, ResNet) for better accuracy
2. **Mobile App**: Develop Android/iOS app for better camera integration
3. **Multi-Language Support**: Voice alerts in regional languages
4. **Barcode/QR Scanning**: Supplement AI with barcode verification

## 10.2 Medium-Term (1-2 years)

1. **Hardware Integration**: Connect with actual pill dispenser hardware
2. **Facial Recognition**: Patient identification before medicine access
3. **Multiple Tablet Detection**: Identify multiple tablets in single image
4. **Offline Mode**: Core verification works without internet

## 10.3 Long-Term (2+ years)

1. **IoT Sensors**: Temperature, humidity sensors for medicine storage
2. **Predictive Analytics**: Predict likely missed doses based on patterns
3. **Integration with Healthcare Systems**: Connect with hospital databases
4. **AI Chatbot**: Natural language interaction for queries
5. **Wearable Integration**: Sync with smartwatches for reminders

## 10.4 Research Extensions

1. **Few-Shot Learning**: Identify new tablets with minimal training images
2. **Explainable AI**: Show why AI made specific prediction
3. **Adverse Reaction Detection**: Alert for dangerous drug combinations
4. **Personalization**: Adapt interface based on user preferences

---

# 11. Conclusion

The **AI-Based Smart Medicine Dispenser** system addresses a critical healthcare challenge by combining simple web technologies with artificial intelligence. This project demonstrates how accessible technologies like Flask, SQLite, OpenCV, and CNN can be integrated to create a practical medical assistance solution.

## Key Achievements

1. **Problem Solved**: Medication errors are prevented through AI-powered tablet verification
2. **User-Centric Design**: Simple interfaces accommodate elderly and non-technical users
3. **Complete Lifecycle**: From registration to monitoring, the system covers all aspects of medication management
4. **Academic Viability**: Uses technologies appropriate for final-year project scope

## Technical Contributions

1. Implementation of image-based medicine verification using CNN
2. Real-time decision module with voice alert integration
3. Comprehensive logging and reporting dashboard
4. MVC architecture using Flask and SQLite

## Social Impact

This system can improve medication compliance, reduce healthcare costs due to medication errors, and provide peace of mind to patients and their families. While this is a prototype-level implementation, the concepts demonstrated can be extended and deployed in real healthcare settings.

## Final Remarks

The AI-Based Smart Medicine Dispenser project successfully showcases the application of artificial intelligence in healthcare, demonstrating that even with limited resources and academic-level tools, meaningful solutions can be developed. Future enhancements can transform this prototype into a production-ready system capable of serving patients in homes, hospitals, and care facilities.

---

# Appendix A: Route-Template-Database Mapping

| Flask Route | HTTP Method | Jinja2 Template | Database Tables |
|------------|-------------|-----------------|-----------------|
| `/` | GET | `index.html` | - |
| `/caretaker/register` | GET, POST | `caretaker/register.html` | Caretaker |
| `/caretaker/login` | GET, POST | `caretaker/login.html` | Caretaker |
| `/caretaker/dashboard` | GET | `caretaker/dashboard.html` | Patient, Schedule, Log |
| `/caretaker/add-patient` | GET, POST | `caretaker/add_patient.html` | Patient |
| `/caretaker/patient/<id>` | GET | `caretaker/patient_detail.html` | Patient, Medicine |
| `/caretaker/patient/<id>/add-medicine` | GET, POST | `caretaker/add_medicine.html` | Medicine, Schedule |
| `/caretaker/medicine/<id>/upload-image` | GET, POST | `caretaker/upload_image.html` | TabletImage |
| `/caretaker/reports` | GET, POST | `caretaker/reports.html` | Log, Patient |
| `/patient/login` | GET, POST | `patient/login.html` | Patient |
| `/patient/dashboard` | GET | `patient/dashboard.html` | Schedule |
| `/patient/take-medicine` | GET | `patient/take_medicine.html` | Schedule, Medicine |
| `/api/capture-image` | POST | - (JSON) | - |
| `/api/verify-tablet` | POST | - (JSON) | Log |
| `/api/process-decision` | POST | - (JSON) | Schedule, Log |

---

# Appendix B: Project File Structure

```
ai_medicine_dispenser/
│
├── app.py                      # Flask application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
│
├── models/
│   ├── __init__.py
│   ├── caretaker.py           # Caretaker model
│   ├── patient.py             # Patient model
│   ├── medicine.py            # Medicine model
│   ├── schedule.py            # Schedule model
│   ├── tablet_image.py        # TabletImage model
│   └── log.py                 # Log model
│
├── routes/
│   ├── __init__.py
│   ├── main.py                # Main routes
│   ├── caretaker.py           # Caretaker routes
│   ├── patient.py             # Patient routes
│   └── api.py                 # API routes
│
├── services/
│   ├── __init__.py
│   ├── ai_service.py          # AI verification logic
│   ├── decision_service.py    # Decision module
│   └── alert_service.py       # Voice alert logic
│
├── static/
│   ├── css/
│   │   └── style.css          # Custom styles
│   ├── js/
│   │   ├── camera.js          # Camera handling
│   │   ├── voice.js           # Voice alerts
│   │   └── main.js            # General scripts
│   └── images/
│
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Home page
│   ├── caretaker/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── add_patient.html
│   │   ├── add_medicine.html
│   │   ├── upload_image.html
│   │   └── reports.html
│   └── patient/
│       ├── login.html
│       ├── dashboard.html
│       └── take_medicine.html
│
├── uploads/
│   └── tablets/               # Tablet images storage
│
├── ml_model/
│   ├── train_model.py         # Model training script
│   ├── predict.py             # Prediction script
│   └── model.h5               # Trained model file
│
└── instance/
    └── database.db            # SQLite database file
```

---

# Appendix C: Sample Code Snippets (Conceptual)

## Flask Route Example (Caretaker - Add Patient)

```python
@caretaker_bp.route('/add-patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        conditions = request.form['conditions']
        
        patient = Patient(
            caretaker_id=current_user.id,
            name=name,
            age=age,
            gender=gender,
            medical_conditions=conditions
        )
        db.session.add(patient)
        db.session.commit()
        
        flash('Patient added successfully!', 'success')
        return redirect(url_for('caretaker.dashboard'))
    
    return render_template('caretaker/add_patient.html')
```

## JavaScript Camera Capture Example

```javascript
async function startCamera() {
    const video = document.getElementById('camera-feed');
    const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
    });
    video.srcObject = stream;
}

function captureImage() {
    const video = document.getElementById('camera-feed');
    const canvas = document.getElementById('capture-canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg');
    sendToServer(imageData);
}
```

## AI Prediction Example (Conceptual)

```python
def predict_tablet(image_path):
    # Load and preprocess image
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))
    image = image / 255.0  # Normalize
    image = np.expand_dims(image, axis=0)
    
    # Load model and predict
    model = load_model('ml_model/model.h5')
    predictions = model.predict(image)
    
    # Get result
    class_index = np.argmax(predictions[0])
    confidence = predictions[0][class_index] * 100
    medicine_name = CLASS_LABELS[class_index]
    
    return medicine_name, confidence
```

---

*Document prepared for Final Year Project submission*
*AI-Based Smart Medicine Dispenser System*
*© 2026*
