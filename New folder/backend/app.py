import os
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import requests # Used for external API calls (email, WhatsApp)

# --- CONFIGURATION ---
class Config:
    # Database configuration (using SQLite for a simple example)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///civiccare.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Set the escalation timers (in hours)
    ESCALATION_TIMER_1 = 48  # Local Officer -> District Officer (48 hours)
    ESCALATION_TIMER_2 = 96  # District Officer -> News/NGOs (96 hours)

# --- INITIALIZATION ---
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
scheduler = BackgroundScheduler()

# --- DATABASE MODEL ---
class IssueReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    place_name = db.Column(db.String(255))
    status = db.Column(db.String(50), default='New') # New, Resolved, Escalated_1, Escalated_2
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    escalation_1_due = db.Column(db.DateTime)
    escalation_2_due = db.Column(db.DateTime)
    officer_email = db.Column(db.String(255)) # Local officer to receive the report

# Initialize the database and scheduler
with app.app_context():
    db.create_all()
    # Start the job scheduler
    scheduler.add_job(func=check_for_escalations, trigger="interval", minutes=10)
    scheduler.start()


# --- SERVICE MOCKUP FUNCTIONS ---
# NOTE: In a real application, these would be complex functions integrating with external APIs.

def get_local_officer_info(lat, lng):
    """Mocks finding the local officer's contact based on location."""
    # This is where you'd query a geofencing service or a static database.
    return {
        'email': 'local.officer@municipality.gov',
        'whatsapp_id': '+919876543210',
        'district_email': 'district.chief@gov.in'
    }

def send_notification(destination, message):
    """Mocks sending a notification (Email, WhatsApp, or Internal Dashboard update)."""
    # Replace with real API calls (e.g., SendGrid, Twilio, etc.)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] NOTIFICATION SENT to {destination}: {message[:50]}...")
    return True

def auto_publish_to_media(report):
    """Mocks publishing the unresolved issue to news channels and NGOs."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] AUTO-PUBLISH: Report {report.report_id} escalated to media/NGOs.")
    # Real logic:
    # 1. Email pre-approved local news outlets and NGOs.
    # 2. Post to a public transparency API.
    send_notification("news@channel.com", f"URGENT UNRESOLVED ISSUE: {report.description}")
    send_notification("ngo@support.org", f"URGENT UNRESOLVED ISSUE: {report.description}")


# --- ESCALATION LOGIC ---

def check_for_escalations():
    """Scheduled job to check all open reports for overdue escalations."""
    with app.app_context():
        now = datetime.utcnow()

        # 1. Check for Escalation 2 (Unresolved after timer 2)
        # Status 'Escalated_1' and escalation_2_due has passed
        reports_to_escalate_2 = IssueReport.query.filter(
            IssueReport.status == 'Escalated_1',
            IssueReport.escalation_2_due < now
        ).all()
        for report in reports_to_escalate_2:
            auto_publish_to_media(report)
            report.status = 'Escalated_2'
            db.session.commit()

        # 2. Check for Escalation 1 (Unresolved after timer 1)
        # Status 'New' and escalation_1_due has passed
        reports_to_escalate_1 = IssueReport.query.filter(
            IssueReport.status == 'New',
            IssueReport.escalation_1_due < now
        ).all()
        for report in reports_to_escalate_1:
            officer_info = get_local_officer_info(report.latitude, report.longitude)
            send_notification(
                officer_info['district_email'],
                f"ESCALATION: Issue {report.report_id} unresolved by local officer. Forwarding to District Officer."
            )
            # Set the next escalation timer
            report.escalation_2_due = now + timedelta(hours=Config.ESCALATION_TIMER_2)
            report.status = 'Escalated_1'
            db.session.commit()


# --- API ROUTES ---

@app.route('/api/report', methods=['POST'])
def submit_report():
    data = request.json
    
    # Required data check (from frontend form)
    if not all(k in data for k in ('description', 'category', 'location')):
        return jsonify({"message": "Missing required fields"}), 400

    # Parse location and get officer info
    try:
        lat, lng = map(float, data['location'].split(','))
        officer_info = get_local_officer_info(lat, lng)
    except Exception:
        return jsonify({"message": "Invalid location format"}), 400

    # 1. INITIAL FORWARDING
    initial_due = datetime.utcnow() + timedelta(hours=Config.ESCALATION_TIMER_1)
    
    new_report = IssueReport(
        report_id=str(int(time.time() * 1000)), # Simple unique ID
        description=data['description'],
        category=data['category'],
        latitude=lat,
        longitude=lng,
        place_name=data.get('place', 'Location unknown'),
        officer_email=officer_info['email'],
        escalation_1_due=initial_due
    )
    db.session.add(new_report)
    db.session.commit()

    # Send initial notification to Local Officer (Email/WhatsApp/Dashboard)
    notification_msg = f"New {new_report.category} report ({new_report.report_id}) at {new_report.place_name}. Description: {new_report.description}. Action required by {initial_due.strftime('%Y-%m-%d %H:%M')}"

    # Forwarding steps
    send_notification(officer_info['email'], notification_msg) # Email
    send_notification(officer_info['whatsapp_id'], notification_msg) # WhatsApp (via API)
    # Note: Internal dashboard update would happen by officer polling or a websocket.

    return jsonify({
        "message": "Report submitted and forwarded to local municipality officer.",
        "report_id": new_report.report_id,
        "escalation_due": initial_due.isoformat()
    }), 201

# --- RUNNER ---
if __name__ == '__main__':
    print("Backend server starting...")
    print(f"Escalation 1 Timer: {Config.ESCALATION_TIMER_1} hours")
    print(f"Escalation 2 Timer: {Config.ESCALATION_TIMER_2} hours")
    # For production, use a proper WSGI server (e.g., Gunicorn)
    app.run(debug=True, port=5000, use_reloader=False) # use_reloader=False is crucial for APScheduler