from flask import Flask, request, jsonify, render_template, send_from_directory
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
from astar import AStar
import webbrowser
import threading
import os

app = Flask(__name__,
            static_folder='../frontend',
            template_folder='../frontend/templates')

# Custom static route to handle frontend files
@app.route('/frontend/<path:path>')
def serve_frontend(path):
    frontend_path = os.path.join(app.root_path, '../frontend')
    return send_from_directory(frontend_path, path)

# ===== 1. Load Room Coordinates (Dynamic + Static) =====
try:
    coord_data = np.load('wifi_data.npz')
    ROOM_COORDINATES = {
        loc: (x, y) for loc, x, y in 
        zip(coord_data['locations'], coord_data['X'], coord_data['Y'])
    }
    # Ensure all required rooms are included
    required_rooms = {
        "Opening": (12.51, 12.0)
    }
    for room, coord in required_rooms.items():
        if room not in ROOM_COORDINATES:
            ROOM_COORDINATES[room] = coord
except (FileNotFoundError, KeyError):
    print("⚠️ Warning: 'wifi_data.npz' missing or invalid. Using static coordinates.")
    ROOM_COORDINATES = {
        "Stair_1": (12.51, 18.75),
        "C205": (11.41, 19),
        "C206": (9.29, 19),
        "C207": (5.5, 19),
        "C208": (0, 17.14),
        "C209": (0, 8.5),
        "C210": (0, 2.8),
        "Stair_2": (0, 0),
        "C201": (4.28, 0),
        "Hallway": (9.29, 0),
        "C202": (11.01, 0),
        "Washroom": (12.51, 0),
        "C203": (12.51, 8.5),
        "Lab": (12.51, 16.9),
        "Opening": (12.51, 12.0)
    }

# ===== 2. Load DNN Model for Location Prediction =====
custom_objects = {'mse': MeanSquaredError()}
dnn_model = load_model('dnn_location.h5', custom_objects=custom_objects)

# ===== 3. Configure Floor Map Grid =====
floor_grid = np.zeros((25, 20))  # 25 rows (Y), 20 columns (X)
# Adjusted obstacles to match the screenshot: only black areas are obstacles
# Adjusted obstacles to match the screenshot: only black areas are obstacles
floor_grid[0:5, 0:20] = 1    # Top barrier (Washroom, C202, C201, Stair_2)
floor_grid[10:15, 5:15] = 1  # Middle block (Opening area)
floor_grid[12, 10] = 0       # ✅ Doorway in middle wall
floor_grid[20:25, 0:20] = 1  # Bottom barrier (C205, C206, C207, C208)
floor_grid[5:20, 0] = 1      # Left wall (C203, Lab, C209, C210)
floor_grid[5:20, 19] = 1     # Right wall (C201, Stair_2, C209, C208)



# Function to print the floor grid
def print_floor_grid():
    print("\nFloor Grid (1 = obstacle, 0 = walkable):")
    print("Y\\X ", end="")
    for x in range(floor_grid.shape[1]):
        print(f"{x:2d}", end=" ")
    print()
    for y in range(floor_grid.shape[0]):
        print(f"{y:2d} ", end="")
        for x in range(floor_grid.shape[1]):
            print(f"{int(floor_grid[y, x]):2d}", end=" ")
        print()

# Print the grid when starting
print_floor_grid()

# ===== 4. Navigation Endpoint =====
@app.route('/navigate', methods=['POST'])
def navigate():
    data = request.json

    print_floor_grid()

    # 1. Predict user's current location using WiFi RSSI
    rssi = np.array([
        data['rssi1'], data['rssi2'],
        data['rssi3'], data['rssi4']
    ]).reshape(1, -1)
    current_pos = dnn_model.predict(rssi, verbose=0)[0]

    # 2. Get destination coordinates
    destination = data['destination']
    if destination not in ROOM_COORDINATES:
        return jsonify({'error': 'Invalid destination'}), 400

    dest_x, dest_y = ROOM_COORDINATES[destination]

    # 3. Convert real-world coordinates to grid system
    SCALE_X, SCALE_Y = 20 / 12.51, 25 / 19  # Grid size is 20x25
    start_grid = (int(current_pos[0] * SCALE_X), int(current_pos[1] * SCALE_Y))
    end_grid = (int(dest_x * SCALE_X), int(dest_y * SCALE_Y))

    # Ensure start and end points are within grid bounds and walkable
    start_grid = (max(1, min(18, start_grid[0])), max(5, min(19, start_grid[1])))
    end_grid = (max(1, min(18, end_grid[0])), max(5, min(19, end_grid[1])))
    while floor_grid[start_grid[1], start_grid[0]] == 1:
        start_grid = (start_grid[0] + 1, start_grid[1])  # Adjust to nearest walkable
    while floor_grid[end_grid[1], end_grid[0]] == 1:
        end_grid = (end_grid[0] + 1, end_grid[1])  # Adjust to nearest walkable

    print(f"Start Grid: {start_grid}")
    print(f"End Grid: {end_grid}")
    print(f"Start walkable: {floor_grid[start_grid[1], start_grid[0]] == 0}")
    print(f"End walkable: {floor_grid[end_grid[1], end_grid[0]] == 0}")
    # 4. Find shortest path using A* algorithm
    astar = AStar(floor_grid)
    path = astar.find_path(start_grid, end_grid)

    if not path:
        return jsonify({'error': 'No valid path found'}), 400

    # 5. Convert grid path to pixel coordinates based on image size (2000x2000)
    IMAGE_WIDTH = 2000  # Matches Figma export width
    IMAGE_HEIGHT = 2000  # Matches Figma export height
    pixel_path = [(int(x * (IMAGE_WIDTH / 20)), int((24 - y) * (IMAGE_HEIGHT / 25))) for x, y in path]
    # (24 - y) flips the Y-axis to match SVG coordinates (top-left origin)

    return jsonify({
        'current': current_pos.tolist(),
        'path': pixel_path,
        'distance': len(path)
    })

# ===== 5. Frontend Routes =====
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/map')
def show_map():
    return render_template('map.html')

# ===== 6. Auto-Launch Browser on Start =====
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run(debug=True)