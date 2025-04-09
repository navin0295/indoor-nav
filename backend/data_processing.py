import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Load the cleaned CSV
df = pd.read_csv('wifi_rssi_data.csv')

# Verify columns
print("Columns in CSV:", df.columns.tolist())

# Extract features - use EXACT column names from above output
X = df[['RSSI_AP1', 'RSSI_AP2', 'RSSI_AP3', 'RSSI_AP4']].values
y = df[['X', 'Y']].values

# Process data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
np.savez('wifi_data.npz', 
         X_train=X_train, X_test=X_test,
         y_train=y_train, y_test=y_test)

print("✅ Data processed successfully!")
print(f"Shape of training data: {X_train.shape}")
print(f"Shape of test data: {X_test.shape}")