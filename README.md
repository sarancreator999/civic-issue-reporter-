# 🌿 CivicCare: Automated Civic Issue Reporting System

CivicCare is a single-page application (SPA) combined with a robust backend API designed to report, track, and automatically escalate local civic issues based on predefined time limits.

---

## ✨ Features

* **Issue Submission:** Users can submit issues with a description, category, and precise geographical location (via Geolocation or map click).
* **Photo Support:** Drag-and-drop support for photo uploads (client-side only for this demo).
* **Interactive Map:** Displays all reported issues using Leaflet.js with Satellite/Street map layers.
* **Automatic Forwarding (Backend):**
    * **Level 0:** Immediate notification to the **Local Municipality Officer**.
    * **Level 1 Escalation:** If unresolved after **48 hours**, the issue is automatically forwarded to the **District Officer**.
    * **Level 2 Escalation:** If still unresolved after an additional **96 hours**, the issue is auto-forwarded to **Local News Channels and NGOs**.
* **Multilingual UI:** Supports English and Tamil language switching in the frontend.
* **Local Storage (Frontend Demo):** The frontend retains reports locally until a backend server is connected.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Leaflet.js
* **Backend (API):** Python, Flask
* **Database:** SQLAlchemy (configured for SQLite in the demo)
* **Job Scheduling:** APScheduler (for handling escalation timers)
* **Configuration:** python-dotenv (for environment variables)

---

## 🚀 Setup and Installation

Follow these steps to get the project running locally.

### 1. Backend Setup

The backend handles issue persistence and the core escalation logic.

1.  **Clone the Repository (Conceptual):**
    ```bash
    # Replace with your actual repository URL
    git clone [repository-url]
    cd civiccare-backend
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create the Configuration File (`.env`):**
    Create a file named `.env` in the root of your backend directory and populate it with the required variables.

    ```env
    # .env file content
    FLASK_APP=app.py
    FLASK_ENV=development

    DATABASE_URL=sqlite:///civiccare.db
    SECRET_KEY="YOUR_SUPER_SECURE_SECRET_KEY"

    # Escalation Timers (in hours)
    ESCALATION_TIMER_1_HOURS=48
    ESCALATION_TIMER_2_HOURS=96

    # MOCK CREDENTIALS (for real-world integration)
    EMAIL_API_KEY="YOUR_SENDGRID_API_KEY"
    TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ```

5.  **Run the Flask Server:**
    The server will automatically create the SQLite database (`civiccare.db`) on the first run and start the APScheduler background job.

    ```bash
    python app.py
    ```
    The API should be running at `http://127.0.0.1:5000`.

### 2. Frontend Setup

The frontend is a single HTML file and should be served alongside the backend.

1.  **Placement:** Ensure the `index.html` file (the provided frontend code) is configured to send `POST` requests to the correct backend endpoint (`/api/report`).
    *(In a full setup, you would typically serve the HTML statically from the Flask app or use a proxy like Nginx to handle routing.)*

2.  **Access:** Open your browser and navigate to the location where the frontend is being served (e.g., `http://127.0.0.1:5000/` if served by Flask).

---

## 📂 Project Structure (Conceptual)