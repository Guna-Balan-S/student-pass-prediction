import streamlit as st
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ABC Public School",
    page_icon="🏫",
    layout="wide"
)

# ---------------- SCHOOL THEME ----------------
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

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center;'>🏫 ABC PUBLIC SCHOOL</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Academic Management System</h4>", unsafe_allow_html=True)

academic_year = f"{datetime.now().year}-{datetime.now().year+1}"
st.markdown(f"<p style='text-align:center;'><b>Academic Year:</b> {academic_year}</p>", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
def login():
    st.subheader("🔐 Login Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Login As", ["Admin", "Teacher"])

    if st.button("Login"):
        if role == "Admin" and username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "Admin"
            st.rerun()

        elif role == "Teacher" and username == "teacher" and password == "teacher123":
            st.session_state.logged_in = True
            st.session_state.role = "Teacher"
            st.rerun()

        else:
            st.error("Invalid Credentials")

# ---------------- REPORT CARD ----------------
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

# ---------------- MAIN ----------------
if not st.session_state.logged_in:
    login()

else:
    st.sidebar.success(f"Logged in as {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # 🔐 ROLE-BASED ACCESS
    if st.session_state.role == "Admin":
        page = st.sidebar.selectbox("Navigation", ["Student View", "Teacher Dashboard"])
    else:
        page = "Teacher Dashboard"

    # ================= STUDENT VIEW (ADMIN ONLY) =================
    if page == "Student View":

        st.subheader("🎓 Student Evaluation Portal")

        model = joblib.load("model/grade_model.pkl")
        scaler = joblib.load("model/scaler.pkl")
        encoder = joblib.load("model/label_encoder.pkl")

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
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                fig, ax = plt.subplots(figsize=(6,4))
                ax.bar(subjects, marks, color="#1976d2")
                st.pyplot(fig)

        total_marks = sum(marks)
        max_marks = num_subjects * 100
        percentage = (total_marks / max_marks) * 100

        internal_marks = st.number_input("Internal Marks", min_value=0.0)

        total_working_days = st.number_input("Total Working Days", min_value=1, value=200)
        leaves = st.number_input("Number of Leaves Taken", min_value=0)

        attendance_percentage = ((total_working_days - leaves) / total_working_days) * 100
        st.info(f"📅 Attendance Percentage: {attendance_percentage:.2f}%")

        if st.button("Generate Result"):

            fail_reasons = []
            suggestions = []

            # Subject check
            for subject, mark in zip(subjects, marks):
                if mark < 35:
                    fail_reasons.append(f"{subject} mark below 35")
                    suggestions.append(f"Increase {subject} mark above 35")

            # Attendance rule
            if attendance_percentage < 75:
                fail_reasons.append(f"Attendance below 75% ({attendance_percentage:.2f}%)")
                suggestions.append("Improve attendance above 75%")

            # Internal marks
            if internal_marks < 10:
                fail_reasons.append("Internal marks too low")
                suggestions.append("Improve internal assessment")

            # AI Prediction
            features = np.array([[total_marks, internal_marks, leaves]])
            scaled = scaler.transform(features)
            prediction = model.predict(scaled)
            grade = encoder.inverse_transform(prediction)[0]

            if grade == "D":
                fail_reasons.append("Low academic performance predicted by AI")
                suggestions.append("Improve total + internal marks")

            status = "FAIL" if fail_reasons else "PASS"

            st.success(f"Total Marks: {total_marks}")
            st.success(f"Percentage: {percentage:.2f}%")
            st.success(f"Grade: {grade}")

            if status == "FAIL":
                st.error("❌ FINAL STATUS: FAIL")

                st.markdown("### 📌 Why You Failed:")
                for r in fail_reasons:
                    st.warning(f"- {r}")

                st.markdown("### 💡 What You Need To Pass:")
                for s in suggestions:
                    st.info(f"- {s}")

            else:
                st.success("✅ FINAL STATUS: PASS")
                st.balloons()

            if student_name:
                file = generate_report_card(student_name, subjects, marks, total_marks, percentage, grade, status)
                with open(file, "rb") as f:
                    st.download_button("📑 Download Report Card", f, file_name=file)

    # ================= TEACHER DASHBOARD =================
    elif page == "Teacher Dashboard":

        st.subheader("📊 Teacher Dashboard")

        uploaded_file = st.file_uploader("Upload Student CSV", type=["csv"])

        if uploaded_file:
            df = pd.read_csv(uploaded_file)

            show_failed_only = st.checkbox("Show Only Failed Students")

            df["StatusIcon"] = df["Status"].apply(
                lambda x: "❌ FAIL" if x == "FAIL" else "✅ PASS"
            )

            if show_failed_only:
                df = df[df["Status"] == "FAIL"]

            def highlight_fail(row):
                if row["Status"] == "FAIL":
                    return ["background-color: #ffcccc"] * len(row)
                return [""] * len(row)

            styled_df = df.style.apply(highlight_fail, axis=1)

            st.dataframe(styled_df, use_container_width=True)

            if len(df) > 0:
                class_average = df["TotalMarks"].mean()
                pass_percentage = (df["Status"] == "PASS").mean() * 100

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Students", len(df))
                col2.metric("Class Average", round(class_average, 2))
                col3.metric("Pass %", f"{round(pass_percentage, 2)}%")

                st.markdown("### 🎖 Grade Distribution")

                grade_counts = df["Grade"].value_counts().sort_index()

                col1, col2, col3 = st.columns([1,2,1])
                with col2:
                    fig, ax = plt.subplots(figsize=(6,4))
                    ax.bar(
                        grade_counts.index,
                        grade_counts.values,
                        color=["#4CAF50", "#2196F3", "#FF9800", "#F44336"]
                    )
                    st.pyplot(fig)
