import streamlit as st
import json
import os
from datetime import datetime

FILE_NAME = "attendancemanagement_data.json"
FACULTY_PASSWORD = "admin123"

st.set_page_config(page_title="Attendance Management - Cyber Cyan Edition", layout="centered")

# --- CYBER CYAN DARK THEME CSS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #F9FAFB;
    }
    .card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #374151;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #374151;
        text-align: center;
    }
    h1, h2, h3 {
        color: #06B6D4 !important;
    }
    /* Ensure buttons are fully visible with high contrast */
    .stButton button {
        background-color: #06B6D4 !important;
        color: #121212 !important;
        font-weight: bold;
        border: none;
    }
    .stButton button:hover {
        background-color: #22D3EE !important;
        color: #121212 !important;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #2A2A2A !important;
        color: #F9FAFB !important;
        -webkit-text-fill-color: #F9FAFB !important;
    }
    </style>
""", unsafe_allow_html=True)

DEFAULT_SUBJECTS = [
    "Data Structures", 
    "Computer Networks", 
    "Operating Systems", 
    "Python"
]

def load_data():
    data = {
        "students": {},
        "notice": "Welcome to the Academic Portal! Ensure your attendance stays above 75%."
    }
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as f:
            data = json.load(f)
    
    # Clean up old subjects if present
    for roll, student in data.get("students", {}).items():
        if "subjects" in student:
            new_subs = {}
            for sub in DEFAULT_SUBJECTS:
                if sub in student["subjects"]:
                    new_subs[sub] = student["subjects"][sub]
                else:
                    new_subs[sub] = {"attended": 0, "total": 0}
            student["subjects"] = new_subs
            
    return data

def save_data(data):
    with open(FILE_NAME, 'w') as f:
        json.dump(data, f, indent=4)

def recalculate_totals(student_data):
    for sub in DEFAULT_SUBJECTS:
        student_data["subjects"][sub] = {"attended": 0, "total": 0}

    for log in student_data.get("logs", []):
        if isinstance(log, dict):
            sub = log.get("subject")
            status = log.get("status")
            if sub in student_data["subjects"]:
                student_data["subjects"][sub]["total"] += 1
                if status == "Present":
                    student_data["subjects"][sub]["attended"] += 1

if "portal" not in st.session_state:
    st.session_state.portal = "Home"

def navigate_to(portal_name):
    st.session_state.portal = portal_name

# --- HOME / ROLE SELECTION ---
if st.session_state.portal == "Home":
    st.markdown("<h1 style='text-align: center;'>🎓 ATTENDANCE MGMT</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9CA3AF;'>Campus Attendance & Analytics Portal</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 Faculty / Admin Portal", use_container_width=True):
            navigate_to("Faculty Login")
            st.rerun()
        if st.button("👨‍🎓 Student Dashboard", use_container_width=True):
            navigate_to("Student Dashboard")
            st.rerun()

# --- FACULTY LOGIN ---
elif st.session_state.portal == "Faculty Login":
    st.markdown("<h2>Faculty Authentication</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### Faculty Access Required")
        st.markdown("Enter your security password to proceed")
        pwd = st.text_input("Password", type="password", label_visibility="collapsed")
        
        if st.button("Login to Portal", use_container_width=True):
            if pwd == FACULTY_PASSWORD:
                navigate_to("Teacher Portal")
                st.rerun()
            else:
                st.error("⚠️ Incorrect Password")
        
        if st.button("← Return to Main Menu"):
            navigate_to("Home")
            st.rerun()

# --- TEACHER PORTAL ---
elif st.session_state.portal == "Teacher Portal":
    st.markdown("<h2>Faculty Control Center</h2>", unsafe_allow_html=True)
    data = load_data()

    with st.container():
        st.markdown("### Register New Student")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            r_input = st.text_input("Roll No", placeholder="Roll")
        with col2:
            n_input = st.text_input("Student Name", placeholder="Name")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Add Student"):
                r, n = r_input.strip(), n_input.strip()
                if r and n:
                    if r not in data["students"]:
                        data["students"][r] = {
                            "name": n,
                            "subjects": {sub: {"attended": 0, "total": 0} for sub in DEFAULT_SUBJECTS},
                            "logs": []
                        }
                        save_data(data)
                        st.success("Student added successfully!")
                        st.rerun()
                    else:
                        st.error("⚠️ Roll Number Already Exists")
                else:
                    st.error("⚠️ Fill in both fields")

    st.markdown("---")
    st.markdown("### Log / Update Session")
    
    if not data["students"]:
        st.info("No active students registered.")
    else:
        rolls = list(data["students"].keys())
        selected_roll = st.selectbox("Select Roll Number", rolls)
        selected_sub = st.selectbox("Select Subject", DEFAULT_SUBJECTS)
        session_date = st.date_input("Date", datetime.now()).strftime("%Y-%m-%d")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✔ Mark Present", use_container_width=True):
                logs = data["students"][selected_roll].get("logs", [])
                existing = next((l for l in logs if l.get("date") == session_date and l.get("subject") == selected_sub), None)
                if existing:
                    existing["status"] = "Present"
                else:
                    logs.append({"date": session_date, "subject": selected_sub, "status": "Present"})
                data["students"][selected_roll]["logs"] = logs
                recalculate_totals(data["students"][selected_roll])
                save_data(data)
                st.success("Attendance updated!")
                st.rerun()
        with col2:
            if st.button("✖ Mark Absent", use_container_width=True):
                logs = data["students"][selected_roll].get("logs", [])
                existing = next((l for l in logs if l.get("date") == session_date and l.get("subject") == selected_sub), None)
                if existing:
                    existing["status"] = "Absent"
                else:
                    logs.append({"date": session_date, "subject": selected_sub, "status": "Absent"})
                data["students"][selected_roll]["logs"] = logs
                recalculate_totals(data["students"][selected_roll])
                save_data(data)
                st.success("Attendance updated!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Live Class Attendance Overview")
    if data["students"]:
        summary_data = []
        for roll, info in data["students"].items():
            name = info.get("name")
            for sub, stats in info.get("subjects", {}).items():
                att = stats.get("attended", 0)
                tot = stats.get("total", 0)
                pct = f"{int((att/tot)*100)}%" if tot > 0 else "0%"
                summary_data.append({
                    "Roll No": roll,
                    "Name": name,
                    "Subject": sub,
                    "Attended": att,
                    "Total": tot,
                    "Percentage": pct
                })
        st.dataframe(summary_data, use_container_width=True)
    else:
        st.info("No records to display yet.")

    st.markdown("---")
    st.markdown("### 📅 Attendance Log History (With Dates)")
    all_logs = []
    for roll, info in data["students"].items():
        for log in info.get("logs", []):
            if isinstance(log, dict):
                all_logs.append({
                    "Date": log.get("date"),
                    "Roll No": roll,
                    "Name": info.get("name"),
                    "Subject": log.get("subject"),
                    "Status": log.get("status")
                })
    if all_logs:
        all_logs = sorted(all_logs, key=lambda x: x["Date"], reverse=True)
        st.dataframe(all_logs, use_container_width=True)
    else:
        st.info("No attendance logs recorded yet.")
        st.markdown("---")
    if st.button("🗑️ Reset All Attendance Data", use_container_width=True):
        if os.path.exists(FILE_NAME):
            os.remove(FILE_NAME)
        st.success("All attendance records have been completely wiped.")
        st.rerun()
    st.markdown("---")
    if st.button("← Return to Main Menu"):
        navigate_to("Home")
        st.rerun()

# --- STUDENT DASHBOARD ---
elif st.session_state.portal == "Student Dashboard":
    st.markdown("<h2>Student Dashboard</h2>", unsafe_allow_html=True)
    data = load_data()

    roll_input = st.text_input("Enter your Roll Number")

    if roll_input:
        roll = roll_input.strip()
        if roll not in data["students"]:
            st.error("⚠️ Student Roll Number Not Found")
        else:
            stu = data["students"][roll]
            subs = stu["subjects"]
            logs = [l for l in stu.get("logs", []) if isinstance(l, dict)]

            total_att = sum(s["attended"] for s in subs.values())
            total_lec = sum(s["total"] for s in subs.values())
            overall_pct = int((total_att / total_lec) * 100) if total_lec > 0 else 0

            st.markdown(f"### Hi, {stu['name']}")
            st.metric(label="Overall Attendance Percentage", value=f"{overall_pct}%", delta=f"{total_att}/{total_lec} Lectures")

            if total_lec > 0 and overall_pct < 75:
                needed = max(0, (3 * total_lec) - (4 * total_att))
                st.warning(f"⚠️ Attend next {needed} consecutive lectures to reach 75%")

            st.markdown("### Subject Breakdowns")
            for subject, stats in subs.items():
                att, tot = stats["attended"], stats["total"]
                pct = int((att / tot) * 100) if tot > 0 else 0
                st.progress(pct / 100, text=f"{subject}: {att}/{tot} ({pct}%)")

            st.markdown("### Attendance Log Timeline")
            if not logs:
                st.info("No attendance logs recorded yet.")
            else:
                for entry in reversed(logs):
                    status_color = "🟢" if entry.get("status") == "Present" else "🔴"
                    st.write(f"{status_color} **{entry.get('date')}** — {entry.get('subject')} ({entry.get('status')})")

    st.markdown("---")
    if st.button("← Return to Main Menu"):
        navigate_to("Home")
        st.rerun()
