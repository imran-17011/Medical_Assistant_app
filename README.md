# Medical_Assistant_app
# 🏥 Doctor Appointment Booking Backend (FastAPI)

A backend-only **FastAPI application** for managing patient intake, urgency assessment, and doctor appointment booking.  
This project is designed as a foundation for healthcare assistant systems with **session-based data storage** (no database required yet).  

---

## ✨ Features
- ✅ **Welcome Route** – Entry point to the system  
- ✅ **Patient Intake** – Collects patient info (name, age, gender, symptoms)  
- ✅ **Session Management** – Data persists across routes using `SessionMiddleware`  
- ✅ **Doctor Booking** – Select from a predefined list of doctors  
- ✅ **Booking Confirmation** – Displays appointment details  

---

## 🏗 Project Structure
project/
├── main.py # FastAPI app & router includes
├── models/
│ └── schemas.py # (Optional) Pydantic models
├── routes/
│ ├── welcome.py # Welcome route
│ ├── intake.py # Patient intake logic
│ └── book.py # Booking logic
├── templates/ # HTML files (optional if frontend added later)
├── static/ # CSS/JS/images (optional if frontend added later)
└── README.md # Documentation

🚀 Running the App

Start the server using Uvicorn:

uvicorn main:app --reload


Then open your browser at:
👉 http://127.0.0.1:8000


