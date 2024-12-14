from flask import Flask, jsonify, request
import googlemaps

app = Flask(__name__)

# Google Maps API Key
gmaps = googlemaps.Client(key="YOUR_GOOGLE_MAPS_API_KEY")

# Mock data for patients and nurses
patients = []
nurses = []

# Assign patients to nurses based on proximity
def assign_patients_to_nurses(nurse_locations, patient_addresses):
    assignments = {nurse: [] for nurse in nurse_locations}

    for patient in patient_addresses:
        distances = []
        for nurse in nurse_locations:
            result = gmaps.distance_matrix(origins=nurse, destinations=patient, mode="driving")
            distance = result["rows"][0]["elements"][0]["distance"]["value"]  # Distance in meters
            distances.append(distance)
        closest_nurse_index = distances.index(min(distances))
        closest_nurse = nurse_locations[closest_nurse_index]
        assignments[closest_nurse].append(patient)

    return assignments

# Optimize route for a single nurse
def optimize_route(start_location, patient_addresses):
    if not patient_addresses:
        return {"error": "No patient addresses provided."}

    destination = patient_addresses[-1]
    waypoints = patient_addresses[:-1]

    directions_result = gmaps.directions(
        origin=start_location,
        destination=destination,
        waypoints=waypoints,
        optimize_waypoints=True,
        mode="driving"
    )

    if directions_result:
        route = directions_result[0]
        optimized_waypoints = route.get("waypoint_order", [])
        steps = [
            step["html_instructions"]
            for leg in route["legs"]
            for step in leg["steps"]
        ]
        return {
            "optimized_waypoints": optimized_waypoints,
            "route_steps": steps,
            "total_distance": route["legs"][0]["distance"]["text"],
            "total_duration": route["legs"][0]["duration"]["text"],
        }
    else:
        return {"error": "No route found."}

# Optimize routes for all nurses
def optimize_routes_for_all_nurses():
    nurse_locations = [nurse["location"] for nurse in nurses]
    patient_addresses = [patient["address"] for patient in patients]

    assignments = assign_patients_to_nurses(nurse_locations, patient_addresses)

    optimized_routes = {}
    for nurse_location, assigned_patients in assignments.items():
        optimized_routes[nurse_location] = optimize_route(nurse_location, assigned_patients)

    return optimized_routes


# Flask Endpoints
@app.route('/nurses', methods=['POST'])
def add_nurse():
    """Add a new nurse."""
    data = request.json
    nurse = {"name": data["name"], "location": data["location"]}
    nurses.append(nurse)
    return jsonify({"message": "Nurse added successfully", "nurse": nurse}), 201


@app.route('/nurses', methods=['GET'])
def get_nurses():
    """Retrieve all nurses."""
    return jsonify(nurses), 200


@app.route('/patients', methods=['POST'])
def add_patient():
    """Add a new patient."""
    data = request.json
    patient = {"name": data["name"], "address": data["address"]}
    patients.append(patient)
    return jsonify({"message": "Patient added successfully", "patient": patient}), 201


@app.route('/patients', methods=['GET'])
def get_patients():
    """Retrieve all patients."""
    return jsonify(patients), 200


@app.route('/routes', methods=['GET'])
def get_routes():
    """Generate and retrieve optimized routes for nurses."""
    optimized_routes = optimize_routes_for_all_nurses()
    return jsonify(optimized_routes), 200


# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
