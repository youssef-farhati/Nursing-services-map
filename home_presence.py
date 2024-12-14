import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Step 1: Read data from the text file
file_path = "simulated_usage.txt"  # Replace with the actual path to your file
df = pd.read_csv(file_path)

# Ensure the column names match
# File has columns: Hour, Load_kW
# Convert Hour to numeric feature (e.g., 0 for 00:00, 1 for 01:00, etc.)
df['Hour_Numeric'] = df['Hour'].str.split(':').str[0].astype(int)

# Step 2: Define a threshold for "home" activity
HOME_THRESHOLD = 0.7  # Example threshold, tune based on your data

# Add a column to label data: 1 if Load_kW >= threshold, else 0
df['Is_Home'] = (df['Load_kW'] >= HOME_THRESHOLD).astype(int)

# Step 3: Prepare features (Hour and Load_kW) and target (Is_Home)
X = df[['Hour_Numeric', 'Load_kW']]
y = df['Is_Home']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train a logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Step 5: Evaluate the model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Step 6: Predict future active hours
# Simulated future data for the next 24 hours
future_data = pd.DataFrame({
    "Hour_Numeric": [h for h in range(24)],
    "Load_kW": np.random.uniform(0.3, 1.5, size=24)  # Replace with actual load data if available
})
future_data['Is_Home_Predicted'] = model.predict(future_data)

# Display predictions
print(future_data)
