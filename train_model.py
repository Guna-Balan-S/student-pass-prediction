import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression

# Load dataset
df = pd.read_csv("student_grade_data.csv")

X = df[["TotalMarks", "InternalMarks", "PreviousLeaves"]]
y = df["Grade"]

# Encode grades
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)

# Save everything
joblib.dump(model, "model/grade_model.pkl")
joblib.dump(scaler, "model/scaler.pkl")
joblib.dump(encoder, "model/label_encoder.pkl")

print("Grade Model Saved Successfully!")
