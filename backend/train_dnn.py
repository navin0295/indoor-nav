import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# 1. Load processed data
data = np.load('wifi_data.npz')
X_train, y_train = data['X_train'], data['y_train']

# 2. Build model
model = Sequential([
    Dense(64, activation='relu', input_shape=(4,)),  # 4 RSSI values
    Dense(64, activation='relu'),
    Dense(2)  # X,Y coordinates
])

# 3. Compile and train
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
history = model.fit(X_train, y_train, epochs=100, batch_size=8, validation_split=0.2)

# 4. Save model
model.save('dnn_location.h5')
print("✅ Model trained and saved")