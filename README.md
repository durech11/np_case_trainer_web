# NP Case Trainer

An educational, local clinical reasoning trainer designed for nurse practitioner students. This app helps users work through patient cases in a structured way to practice building differential diagnoses, SOAP notes, and treatment plans.

## ⚠️ Important Safety Notice
**Educational Purpose Only:** This application is for training and educational purposes. It does **not** provide medical advice, diagnosis, or treatment. All content, diagnostic suggestions, and treatment plans are framed as educational guidance and model answers for study purposes.

## Tech Stack
- Python
- FastAPI
- SQLite / SQLModel
- Jinja2 Templates
- Vanilla JS & CSS

## Setup Instructions

1. **Install Dependencies**
   Ensure you have Python 3.9+ installed. Create a virtual environment and install the requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the Application**
   Start the FastAPI server locally using Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access the App**
   Open your browser and navigate to:
   [http://127.0.0.1:8000](http://127.0.0.1:8000)

   You can also check the health endpoint at:
   [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## Directory Structure
- `app/`: Main application code (routes, services, models, core database config).
- `cases/`: Place your structured JSON case studies here.
- `db/`: Local SQLite database storage.
- `static/`: CSS and Vanilla JS files.
- `templates/`: Jinja2 HTML templates.