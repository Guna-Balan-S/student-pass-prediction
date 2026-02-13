import numpy as np
import joblib

model = joblib.load("model/student_model.pkl")
scaler = joblib.load("model/scaler.pkl")

# Take input from user
study_hours = float(input("Enter Study Hours: "))
attendance = float(input("Enter Attendance (%): "))
previous_marks = float(input("Enter Previous Marks: "))

new_student = np.array([[study_hours, attendance, previous_marks]])
new_student_scaled = scaler.transform(new_student)

prediction = model.predict(new_student_scaled)

print("\nResult:", "PASS" if prediction[0] == 1 else "FAIL")
