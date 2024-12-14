from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
from twilio.rest import Client

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for frontend integration

# Twilio setup (replace with your Twilio credentials)
account_sid = "your_account_sid"
auth_token = "your_auth_token"
twilio_client = Client(account_sid, auth_token)

# Global storage for patients and nurses
patients = {}
nurses = {}

# Logistic Regression Model
model = LogisticRegression()

# Load and train model with example data
def train_model():
    df = pd.read_csv("simulated_usage.txt")  # Replace with your data file
    df['Hour_Numeric'] = df['Hour'].str.split(':').str[0].astype(int)
    df['Is_Home'] = (df['Load_kW'] >= 0.7).astype(int)
    X = df[['Hour_Numeric', 'Load_kW']]
    y = df['Is_Home']
    model.fit(X, y)

train_model()

# Twilio Notification Function
def send_notification(phone_number, message):
    twilio_client.messages.create(
        to=phone_number,
        from_="your_twilio_number",  # Replace with your Twilio number
        body=message
    )

# API Endpoints

@app.route('/patients', methods=['POST'])
def add_patient():
    """Add a new patient."""
    data = request.json
    if data["name"] in patients:
        return jsonify({"error": "Patient already exists"}), 400
    patients[data["name"]] = {
        "address": data["address"],
        "phone": data["phone"],
        "electricity_usage": []
    }
    return jsonify({"message": "Patient added successfully"}), 200

@app.route('/patients', methods=['GET'])
def get_patients():
    """Retrieve all patients."""
    return jsonify(patients), 200

@app.route('/patients/<name>/electricity', methods=['POST'])
def add_electricity_usage(name):
    """Add electricity usage data for a patient."""
    if name not in patients:
        return jsonify({"error": "Patient not found"}), 404
    data = request.json
    patients[name]["electricity_usage"].append(data)
    return jsonify({"message": "Electricity data added successfully"}), 200

@app.route('/predict', methods=['POST'])
def predict_activity():
    """Predict if patients are active based on electricity data."""
    data = request.json  # Expects JSON with Hour_Numeric and Load_kW
    input_data = pd.DataFrame(data)
    predictions = model.predict(input_data)
    input_data['Is_Home_Predicted'] = predictions
    return jsonify(input_data.to_dict(orient='records')), 200

@app.route('/routes', methods=['GET'])
def calculate_routes():
    """Calculate routes for nurses based on active patients."""
    active_patients = []
    for patient, details in patients.items():
        if details["electricity_usage"]:
            latest_data = details["electricity_usage"][-1]
            hour_numeric = latest_data["Hour_Numeric"]
            load_kW = latest_data["Load_kW"]
            is_home = model.predict([[hour_numeric, load_kW]])[0]
            if is_home:
                active_patients.append({"name": patient, "address": details["address"]})
                # Notify the nurse
                send_notification(
                    details["phone"],
                    f"{patient} is active and ready for a visit!"
                )
    # Mock route calculation
    nurse_routes = {"nurse_1": active_patients}
    return jsonify(nurse_routes), 200

@app.route('/nurses', methods=['POST'])
def add_nurse():
    """Add a new nurse."""
    data = request.json
    if data["name"] in nurses:
        return jsonify({"error": "Nurse already exists"}), 400
    nurses[data["name"]] = {"assigned_patients": []}
    return jsonify({"message": "Nurse added successfully"}), 200

@app.route('/nurses', methods=['GET'])
def get_nurses():
    """Retrieve all nurses."""
    return jsonify(nurses), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
