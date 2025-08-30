import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import date, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------- Load API & Email ------------------- #
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# ------------------- Doctor Emails (Demo) ------------------- #
# Assigning only your two emails to all doctors
doctor_emails = {
    "Dr. Ahmed": "imranali008800@gmail.com",
    "Dr. Farhan": "nazishjahan22@gmail.com",
    "Dr. Kamran": "imranali008800@gmail.com",
    "Dr. Mumtaz": "nazishjahan22@gmail.com",
    "Dr. Imran": "imranali008800@gmail.com",
    "Dr. Sadam": "nazishjahan22@gmail.com",
    "Dr. Muzafar": "imranali008800@gmail.com",
    "Dr. Nazish": "nazishjahan22@gmail.com",
}

# ------------------- CSS for VIP look ------------------- #
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("assets/flowers.png");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-color: #f0f8ff;
    }
    .user-msg {background-color: #1E3A8A;color: white;padding: 12px;border-radius: 18px;margin: 5px 0;text-align: right;font-size: 16px;}
    .ai-msg {background-color: #E2E8F0;color: #111827;padding: 12px;border-radius: 18px;margin: 5px 0;text-align: left;font-size: 16px;}
    .system-msg {background-color: #D97706;color: white;padding: 12px;border-radius: 12px;margin: 5px 0;text-align: center;font-weight: bold;}
    button {background: linear-gradient(45deg, #1E3A8A, #3B82F6);color: white !important;border-radius: 12px !important;font-weight: bold !important;padding: 10px !important;}
    button:hover {background: linear-gradient(45deg, #3B82F6, #60A5FA);}
    .doctor-card {background-color: #ffffffcc;border-radius: 12px;padding: 10px;margin: 5px;box-shadow: 2px 2px 8px #aaa;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------- Session State ------------------- #
if "users" not in st.session_state: st.session_state["users"] = {}
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = None
if "chat" not in st.session_state: st.session_state["chat"] = []
if "selected_doctor" not in st.session_state: st.session_state["selected_doctor"] = None
if "appointment_date" not in st.session_state: st.session_state["appointment_date"] = date.today()
if "appointment_time" not in st.session_state: st.session_state["appointment_time"] = time(9,0)
if "appointment_done" not in st.session_state: st.session_state["appointment_done"] = False

# ------------------- Utility Functions ------------------- #
def get_gemini_answer(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {e}"

def check_urgency(symptoms: str) -> str:
    urgent_keywords = ["chest pain", "shortness of breath", "severe bleeding", "unconscious", "stroke", "heart attack"]
    if any(word in symptoms.lower() for word in urgent_keywords):
        return "urgent"
    return "non-urgent"

def suggest_doctors(symptoms: str):
    doctors = {
        "chest pain": [{"name": "Dr. Ahmed", "specialty": "Cardiologist"},
                       {"name": "Dr. Farhan", "specialty": "Emergency Physician"}],
        "shortness of breath": [{"name": "Dr. Kamran", "specialty": "Pulmonologist"},
                                {"name": "Dr. Mumtaz", "specialty": "Emergency Physician"}],
        "Anxiety": [{"name": "Dr. Imran", "specialty": "Psychiatrist"},
                     {"name": "Dr. Sadam", "specialty": "Trauma Specialist"}],
        "stroke": [{"name": "Dr. Muzafar", "specialty": "Neurologist"},
                   {"name": "Dr. Ahmed", "specialty": "Emergency Physician"}],
        "headache": [{"name": "Dr. Kamran", "specialty": "Neurologist"},
                     {"name": "Dr. Farhan", "specialty": "General Physician"}],
        "vomiting": [{"name": "Dr. Imran", "specialty": "Gastroenterologist"},
                     {"name": "Dr. Mumtaz", "specialty": "General Physician"}],
        "high bp": [{"name": "Dr. Ahmed", "specialty": "Cardiologist"},
                    {"name": "Dr. Farhan", "specialty": "General Physician"}],
    }
    matches = []
    for key, docs in doctors.items():
        if key in symptoms.lower():
            matches.extend(docs)
    return matches if matches else [{"name": "Dr. Nazish", "specialty": "General Physician"}]

def send_email(to_email, patient_name, doctor_name, appointment_date, appointment_time):
    if not EMAIL_USER or not EMAIL_PASS:
        st.error("⚠️ EMAIL_USER or EMAIL_PASS not set in .env file!")
        return

    subject = "New Appointment Booking"
    body = f"""
    Hello {doctor_name},

    Patient {patient_name} has booked an appointment with you.
    Date: {appointment_date}
    Time: {appointment_time}

    Please prepare accordingly.
    """
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        st.success("✅ Email sent to doctor!")
    except Exception as e:
        st.error(f"⚠️ Error sending email: {e}")

# ------------------- Authentication ------------------- #
def signup_page():
    st.subheader("📝 Sign Up")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    if st.button("Create Account"):
        if username in st.session_state["users"]:
            st.error("⚠️ Username already exists!")
        else:
            st.session_state["users"][username] = password
            st.success("✅ Account created! Please login.")

def login_page():
    st.subheader("🔐 Login")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if st.session_state["users"].get(username) == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome back, {username}!")
        else:
            st.error("❌ Invalid username or password")

# ------------------- Assistant Page ------------------- #
def assistant_page():
    st.title("🩺 AI Medical Assistant")
    st.write(f"Hello, **{st.session_state['username']}** 👋")
    symptoms = st.text_area("Describe your symptoms:")

    if st.button("Ask AI") and symptoms.strip():
        st.session_state["chat"].append({"role": "user", "text": symptoms})

        urgency = check_urgency(symptoms)
        ai_prompt = f"You are a medical assistant. Patient symptoms: {symptoms}. Provide possible causes and next steps."
        ai_response = get_gemini_answer(ai_prompt)
        st.session_state["chat"].append({"role": "assistant", "text": ai_response})

        doctors = suggest_doctors(symptoms)
        if urgency == "urgent":
            st.session_state["chat"].append({"role": "system", "text": "🚨 Urgent case detected! Suggested doctors:"})
        else:
            st.session_state["chat"].append({"role": "system", "text": "✅ Non-Urgent - You may book an appointment if needed."})

        # Store doctors in session_state for persistent selection
        st.session_state["doctors_list"] = doctors

    # Display doctor cards and selection only if doctors are suggested
    if "doctors_list" in st.session_state:
        st.subheader("👨‍⚕️ Suggested Doctors")
        for doc in st.session_state["doctors_list"]:
            st.markdown(
                f"""
                <div class='doctor-card'>
                👨‍⚕️ **{doc['name']}**  
                🏥 {doc['specialty']}  
                </div>
                """,
                unsafe_allow_html=True
            )
        # Persistent doctor selection
        doctor_names = [doc['name'] for doc in st.session_state["doctors_list"]]
        st.session_state["selected_doctor"] = st.selectbox("Select Doctor for Appointment", doctor_names, 
                                                           index=doctor_names.index(st.session_state["selected_doctor"]) if st.session_state["selected_doctor"] in doctor_names else 0)
        selected_doc = next(doc for doc in st.session_state["doctors_list"] if doc['name'] == st.session_state["selected_doctor"])

        # Persistent date & time selection
        st.session_state["appointment_date"] = st.date_input("Select Date", st.session_state["appointment_date"])
        st.session_state["appointment_time"] = st.time_input("Select Time", st.session_state["appointment_time"])

        # Confirm appointment button
        if st.button("Confirm Appointment") and not st.session_state["appointment_done"]:
            st.session_state["appointment_done"] = True
            st.success(f"✅ Appointment booked on {st.session_state['appointment_date']} at {st.session_state['appointment_time']} with {selected_doc['name']}.")
            send_email(
                to_email=doctor_emails[selected_doc['name']],
                patient_name=st.session_state["username"],
                doctor_name=selected_doc['name'],
                appointment_date=st.session_state["appointment_date"],
                appointment_time=st.session_state["appointment_time"]
            )

    # Display chat
    for msg in st.session_state["chat"]:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'>👤 {msg['text']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f"<div class='ai-msg'>🤖 {msg['text']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "system":
            st.markdown(f"<div class='system-msg'>⚡ {msg['text']}</div>", unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["chat"] = []
        st.session_state["selected_doctor"] = None
        st.session_state["appointment_done"] = False
        st.success("✅ Logged out successfully!")

# ------------------- Main ------------------- #
def main():
    st.set_page_config(page_title="AI Medical Assistant", page_icon="🩺", layout="centered")
    if not st.session_state["logged_in"]:
        menu = st.sidebar.radio("Menu", ["Login", "Sign Up"])
        if menu == "Login":
            login_page()
        else:
            signup_page()
    else:
        assistant_page()

if __name__ == "__main__":
    main()
