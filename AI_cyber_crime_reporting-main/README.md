<<<<<<< HEAD
# AI-Enhanced Cybercrime Reporting and Investigation Platform

## 📖 About The Project

This project is an AI-integrated, multi-role web platform designed to bridge the gap between victims of cybercrime and law enforcement investigators. It provides a secure and user-friendly portal for victims to file reports and a powerful, data-driven dashboard for investigators to analyze, prioritize, and manage cases efficiently.

The platform leverages **Google Gemini AI** to provide intelligent features such as case type prediction, automated report refinement, and actionable insights for investigators.

---

## 🛠️ Tech Stack

This project is built with the following technologies:

* **Backend:** Python, Django  
* **Database:** SQLite (for development), PostgreSQL (for production)  
* **Frontend:** HTML, CSS, JavaScript  
* **AI/ML:** Google Gemini AI (Generative AI)  
* **Geocoding:** OpenStreetMap (Nominatim)  
* **Data Visualization:** Chart.js, Leaflet.js (for Heatmaps)

---

## 📂 Project Structure

```text
AI_Cybercrime/
├── cybercrime_platform/    # Project configuration (settings, urls)
├── dashboard/              # Main application logic
│   ├── migrations/         # Database migrations
│   ├── static/             # CSS, JS, and images
│   ├── templates/          # HTML templates
│   ├── models.py           # Database models
│   ├── views.py            # Application views & API logic
│   └── urls.py             # App-specific URL routing
├── media/                  # User-uploaded evidence files
├── venv/                   # Virtual environment (not in repo)
├── .env                    # Environment variables (create manually)
├── db.sqlite3              # Default database
├── manage.py               # Django command-line utility
└── requirement.txt         # Project dependencies
```

---

## ✅ Key Features

### 🛡️ For Victims (Users)

* **Secure Reporting:** File detailed cybercrime reports with automatic case type and department prediction.  
* **AI Assistance:**
  * **CyberShield AI Chatbot:** A compassionate AI assistant to guide victims and answer queries.  
  * **Report Refinement:** Converts rough incident descriptions into formal, professional incident reports.  
* **User Dashboard:** Track case status, view safety tips, and manage profile information.  
* **Secure Messaging:** Two-way, WhatsApp-style chat with investigators for each case.  
* **Evidence Upload:** Securely upload files/evidence related to the case.

### 🕵️‍♂️ For Investigators (Superusers)

* **Investigator Dashboard:** A comprehensive view of all cases with status filtering and priority management.  
* **AI Insights:** Dynamic, AI-generated actionable insights based on current crime statistics.  
* **Crime Heatmap:** Visual representation of crime hotspots based on victim locations.  
* **Analytics:** Real-time charts and statistics (Total Cases, Success Rate, Case Type Breakdown).  
* **Case Management:** Update case status, review evidence, and communicate with victims.  
* **Export Data:** Export complaint data to CSV for offline analysis.

---

## 🚀 Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

* Python 3.x  
* pip  
* A Google Cloud API Key (for Gemini AI)

### Installation

1. **Clone the repo**
    ```sh
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Create and activate a virtual environment**
    ```sh
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On Mac/Linux:
    source venv/bin/activate
    ```

3. **Install dependencies**
    ```sh
    pip install -r requirement.txt
    ```

4. **Set up Environment Variables**
    > [!IMPORTANT]
    > This project requires sensitive API keys to function. These are NOT included in the repository for security.

    * Create a file named `.env` in the project root directory.
    * Add the following keys (replace with your actual values):
        ```env
        # Django Security
        SECRET_KEY=your_generated_secret_key_here
        DEBUG=True

        # AI Configuration (Required)
        GOOGLE_API_KEY=your_gemini_api_key_here

        # Database Configuration (Optional - Defaults to SQLite if omitted)
        # DB_ENGINE=postgresql
        # DB_NAME=cybercrime_db
        # DB_USER=postgres
        # DB_PASSWORD=your_db_password
        # DB_HOST=localhost
        # DB_PORT=5432
        ```

5. **Apply database migrations**
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

6. **Create a superuser (for the Investigator role)**
    ```sh
    python manage.py createsuperuser
    ```

7. **Run the development server**
    ```sh
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

---

## 🔮 Future Roadmap

* [ ] **Advanced Analytics:** Deeper integration with ML libraries for trend forecasting.  
* [ ] **Multi-language Support:** Expand the platform to support regional languages.  
* [ ] **Mobile App:** Develop a dedicated mobile application for easier reporting.  
* [ ] **Blockchain Integration:** For immutable evidence logging.
=======
# AI_cyber_crime_reporting
This project is an AI-integrated, multi-role web platform designed to bridge the gap between victims of cybercrime and law enforcement investigators. It provides a secure and user-friendly portal for victims to file reports and a powerful, data-driven dashboard for investigators to analyze, prioritize, and manage cases efficiently.
>>>>>>> fca4561f326cf8f67f89468c84e10f84104c44d8
