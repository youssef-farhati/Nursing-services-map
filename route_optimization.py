from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
import googlemaps
import datetime

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Google Maps API Key
GMAPS_API_KEY = "your_google_maps_api_key"
gmaps = googlemaps.Client(key=GMAPS_API_KEY)

# Logistic Regression Model
model = LogisticRegression()

# Mock patient data
patients = {
    "John Doe": {"address": "123 Main St, Toronto", "phone": "+123456789", "electricity_usage": []},
    "Jane Smith": {"address": "456 Elm St, Toronto", "phone": "+987654321", "electricity_usage": []},
}

# Load and train model
def train_model():
    df = pd.read_csv("simulated_usage.txt")  # Replace with your data file
    df['Hour_Numeric'] = df['Hour'].str.split(':').str[0].astype(int)
    df['Is_Home'] = (df['Load_kW'] >= 0.7).astype(int)
    X = df[['Hour_Numeric', 'Load_kW']]
    y = df['Is_Home']
    model.fit(X, y)

train_model()

# Predict if the patient is home based on their electricity usage
def is_patient_home(hour_numeric, load_kW):
    return model.predict([[hour_numeric, load_kW]])[0] == 1

@app.route('/')
def index():
    """Render the frontend interface."""
    return render_template("index.html", api_key=GMAPS_API_KEY)

@app.route('/routes', methods=['GET'])
def calculate_routes():
    """Calculate routes for nurses."""
    active_patients = []
    current_time = datetime.datetime.now()

    # Filter active patients based on electricity usage prediction
    for patient, details in patients.items():
        if details["electricity_usage"]:
            latest_data = details["electricity_usage"][-1]
            hour_numeric = latest_data["Hour_Numeric"]
            load_kW = latest_data["Load_kW"]
            
            # Predict if the patient is home
            is_home = is_patient_home(hour_numeric, load_kW)
            if is_home:
                active_patients.append({"name": patient, "address": details["address"]})

    # Nurse's starting location (can be customized)
    nurse_location = "789 Nurse St, Toronto"

    # Calculate the most efficient route using Google Maps Directions API
    if active_patients:
        waypoints = [patient["address"] for patient in active_patients]
        directions_result = gmaps.directions(
            origin=nurse_location,
            destination=waypoints[-1],  # Last patient
            waypoints=waypoints[:-1],  # All intermediate patients
            mode="driving",
            optimize_waypoints=True,  # Optimizes the route for efficiency
            departure_time=current_time
        )

        routes = []
        for route in directions_result[0]['legs']:
            routes.append({
                "name": active_patients[route['start_location']]['name'],
                "address": route['end_address'],
                "directions": route
            })

        return jsonify(routes), 200
    else:
        return jsonify({"message": "No active patients available."}), 200

if __name__ == '__main__':
    app.run(debug=True)
