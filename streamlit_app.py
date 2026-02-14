# ================== IMPORT PACKAGES ==================
import streamlit as st
import numpy as np
import pandas as pd
import joblib
from fpdf import FPDF
from datetime import datetime
import plotly.express as px

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="ABC Public School",
    page_icon="🏫",
    layout="wide"
)

# ================== SCHOOL THEME ==================
st.markdown("""
<style>
.main {background-color: #f4f8fb;}
h1, h2, h3 {color: #0d47a1;}
.stButton>button {
    background-color: #1976d2;
    color: white;
    border-radius: 6px;
    height: 45px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("<h1 style='text-align:center;'>🏫 ABC PUBLIC SCHOOL</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Academic Management System</h4>", unsafe_allow_html=True)

academic_year = f"{datetime.now().year}-{datetime.now().year+1}"
st.markdown(f"<p style='text-align:center;'><b>Academic Year:</b> {academic_year}</p>", unsafe_allow_html=True)

# ================== SESSION INIT ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# ================== LOGIN FUNCTION ==================
def login():
    st.subheader("🔐 Login Portal")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Login As", ["Admin", "Teacher"])

    if st.button("Login"):
        if role == "Admin" and username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "Admin"
            st.session_state.admin_nav = "Student View"  # 🔥 Force default
            st.rerun()

        elif role == "Teacher" and username == "teacher" and password == "teacher123":
            st.session_state.logged_in = True
            st.session_state.role = "Teacher"
            st.rerun()

        else:
            st.error("Invalid Credentials")

# ================== REPORT CARD ==================
def generate_report_card(name, subjects, marks, total, percentage, grade, status):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "ABC PUBLIC SCHOOL", ln=True, align="C")
    pdf.cell(200, 10, "Student Report Card", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, f"Name: {name}", ln=True)
    pdf.cell(200, 8, f"Academic Year: {academic_year}", ln=True)
    pdf.ln(5)

    for subject, mark in zip(subjects, marks):
        pdf.cell(200, 8, f"{subject}: {mark}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 8, f"Total Marks: {total}", ln=True)
    pdf.cell(200, 8, f"Percentage: {percentage:.2f}%", ln=True)
    pdf.cell(200, 8, f"Grade: {grade}", ln=True)
    pdf.cell(200, 8, f"Final Result: {status}", ln=True)

    file_name = f"{name}_ReportCard.pdf"
    pdf.output(file_name)
    return file_name

# ================== MAIN ==================
if not st.session_state.logged_in:
    login()

else:
    st.sidebar.success(f"Logged in as {st.session_state.role}")

    # 🔥 Proper logout reset
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # ================= ROLE CONTROL =================
    # ================= ROLE CONTROL =================
    if st.session_state.role == "Admin":

    # Force default page on first login
        if "page" not in st.session_state:
              st.session_state.page = "Student View"

              st.sidebar.markdown("### Navigation")

        if st.sidebar.button("🎓 Student View"):
              st.session_state.page = "Student View"

        
    elif st.session_state.role == "Teacher":
        st.session_state.page = "Teacher Dashboard"

    else:
        st.stop()

    page = st.session_state.page


    # ================= STUDENT VIEW =================
    if page == "Student View":

        st.subheader("🎓 Student Evaluation Portal")

        try:
            model = joblib.load("model/grade_model.pkl")
            scaler = joblib.load("model/scaler.pkl")
            encoder = joblib.load("model/label_encoder.pkl")
            model_loaded = True
        except:
            model_loaded = False
            st.warning("⚠ AI Model not found. Prediction disabled.")

        student_name = st.text_input("Student Name")
        num_subjects = st.number_input("Number of Subjects", min_value=1)

        subjects = []
        marks = []

        for i in range(int(num_subjects)):
            subject = st.text_input(f"Subject {i+1} Name", key=f"sub{i}")
            mark = st.number_input(f"Marks for Subject {i+1}", min_value=0.0, key=f"mark{i}")
            subjects.append(subject if subject else f"Subject {i+1}")
            marks.append(mark)

        if len(marks) > 0:
            chart_df = pd.DataFrame({"Subject": subjects, "Marks": marks})
            fig = px.bar(chart_df, x="Subject", y="Marks",
                         color="Marks", color_continuous_scale="Blues",
                         title="📊 Subject-wise Performance")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        total_marks = sum(marks)
        max_marks = num_subjects * 100
        percentage = (total_marks / max_marks) * 100 if max_marks else 0

        internal_marks = st.number_input("Internal Marks", min_value=0.0)
        total_working_days = st.number_input("Total Working Days", min_value=1, value=200)
        leaves = st.number_input("Number of Leaves Taken", min_value=0)

        attendance_percentage = ((total_working_days - leaves) / total_working_days) * 100
        st.info(f"📅 Attendance Percentage: {attendance_percentage:.2f}%")

        if st.button("🔮 Predict Result"):

            fail_reasons = []
            suggestions = []

            for subject, mark in zip(subjects, marks):
                if mark < 35:
                    fail_reasons.append(f"{subject} mark below 35")
                    suggestions.append(f"Increase {subject} mark above 35")

            if attendance_percentage < 75:
                fail_reasons.append("Attendance below 75%")
                suggestions.append("Improve attendance above 75%")

            if internal_marks < 10:
                fail_reasons.append("Internal marks too low")
                suggestions.append("Improve internal assessment")

            grade = "N/A"

            if model_loaded:
                features = np.array([[total_marks, internal_marks, leaves]])
                scaled = scaler.transform(features)
                prediction = model.predict(scaled)
                grade = encoder.inverse_transform(prediction)[0]

                if grade == "D":
                    fail_reasons.append("Low academic performance predicted by AI")
                    suggestions.append("Improve total + internal marks")

            status = "FAIL" if fail_reasons else "PASS"

            st.success(f"📊 Total Marks: {total_marks}")
            st.success(f"📈 Percentage: {percentage:.2f}%")
            st.success(f"🏅 Grade: {grade}")

            if status == "FAIL":
                st.error("❌ FINAL STATUS: FAIL")
                for r in fail_reasons:
                    st.warning(f"- {r}")
                for s in suggestions:
                    st.info(f"- {s}")
            else:
                st.success("✅ FINAL STATUS: PASS")
                st.balloons()

    # ================= TEACHER DASHBOARD =================
    elif page == "Teacher Dashboard":

        st.subheader("📊 Teacher Analytics Dashboard")

        uploaded_file = st.file_uploader("Upload Student CSV", type=["csv"])

        if uploaded_file:
            df = pd.read_csv(uploaded_file)

            if "Status" not in df.columns and "Grade" in df.columns:
                df["Status"] = df["Grade"].apply(lambda x: "FAIL" if x == "D" else "PASS")

            st.markdown("## 📌 Class Overview")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("👨‍🎓 Total Students", len(df))
            col2.metric("📈 Class Average", round(df.get("TotalMarks", pd.Series([0])).mean(), 2))
            col3.metric("✅ Pass %", f"{round((df['Status']=='PASS').mean()*100,2) if 'Status' in df else 0}%")
            col4.metric("❌ Fail Count", (df["Status"]=="FAIL").sum() if "Status" in df else 0)

            st.divider()

            if "Grade" in df.columns:
                col1, col2 = st.columns(2)

                grade_counts = df["Grade"].value_counts().reset_index()
                grade_counts.columns = ["Grade", "Count"]

                fig1 = px.bar(grade_counts, x="Grade", y="Count", color="Grade")
                fig1.update_layout(height=350)
                col1.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

                if "Status" in df.columns:
                    status_counts = df["Status"].value_counts().reset_index()
                    status_counts.columns = ["Status", "Count"]

                    fig2 = px.pie(status_counts, names="Status", values="Count", hole=0.5)
                    fig2.update_layout(height=350)
                    col2.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

            st.divider()
            st.dataframe(df, use_container_width=True)
