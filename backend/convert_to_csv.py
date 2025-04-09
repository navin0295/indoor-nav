import pandas as pd

# Read Excel file
df = pd.read_excel('wifi_rssi_data.xlsx')

# Clean column names (remove extra spaces)
df.columns = df.columns.str.strip()

# Save as CSV
df.to_csv('wifi_rssi_data.csv', index=False)
print("✅ Excel converted to CSV successfully!")