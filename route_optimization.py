import googlemaps
from datetime import datetime

# Google Maps API Key
API_KEY = "your_google_maps_api_key"
gmaps = googlemaps.Client(key=API_KEY)

# Example Data: Active Patients
nurse_start_location = "123 Main St, City, Country"  # Nurse's starting location
active_patients = [
    {"name": "Patient A", "address": "456 Elm St, City, Country"},
    {"name": "Patient B", "address": "789 Oak St, City, Country"},
    {"name": "Patient C", "address": "321 Pine St, City, Country"},
]

# Step 1: Calculate Distance Matrix
def calculate_distance_matrix(start, destinations):
    locations = [start] + [patient["address"] for patient in destinations]
    matrix = gmaps.distance_matrix(
        origins=locations,
        destinations=locations,
        mode="driving",
        departure_time=datetime.now()
    )
    return matrix

# Step 2: Solve Traveling Salesperson Problem (TSP)
def solve_tsp(distance_matrix):
    import itertools
    n = len(distance_matrix)
    indices = range(n)
    min_distance = float("inf")
    best_route = None

    for perm in itertools.permutations(indices[1:]):  # Exclude starting point from permutations
        route = [0] + list(perm) + [0]  # Include starting point at beginning and end
        distance = sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
        if distance < min_distance:
            min_distance = distance
            best_route = route

    return best_route, min_distance

# Step 3: Route Optimization
def optimize_routes(nurse_start, patients):
    # Calculate the distance matrix
    matrix = calculate_distance_matrix(nurse_start, patients)
    distances = [
        [row["distance"]["value"] for row in element["elements"]]
        for element in matrix["rows"]
    ]

    # Solve TSP
    route, total_distance = solve_tsp(distances)
    optimized_addresses = [patients[i-1]["address"] for i in route[1:-1]]
    return {
        "optimized_route": [nurse_start] + optimized_addresses + [nurse_start],
        "total_distance_km": total_distance / 1000
    }

# Step 4: Call the Function and Print Results
optimized_route = optimize_routes(nurse_start_location, active_patients)
print("Optimized Route:", optimized_route["optimized_route"])
print("Total Distance (km):", optimized_route["total_distance_km"])
