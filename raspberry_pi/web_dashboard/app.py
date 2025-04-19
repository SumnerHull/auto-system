from flask import Flask, render_template, jsonify, request
import json
import serial
import threading
import time
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lidar_processing.lidar_processor import LidarProcessor

app = Flask(__name__)

# Global variables for car state
car_state = {
    "mode": "manual",  # manual, autonomous, line_following
    "speed": 0,        # -100 to 100
    "steering": 0,     # -100 to 100
    "battery_level": 100,
    "sensor_data": {
        "ultrasonic": {
            "front_left": 0,
            "front_right": 0,
            "back_left": 0,
            "back_right": 0
        },
        "gyro": {},
        "lidar": {}
    }
}

# Initialize LiDAR processor
lidar_processor = None
try:
    lidar_processor = LidarProcessor(port='/dev/ttyUSB0')
    lidar_processor.start()
    print("LiDAR initialized")
except Exception as e:
    print(f"Could not initialize LiDAR: {e}")

# Serial communication with Arduino
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    print("Arduino connected")
except Exception as e:
    print(f"Could not connect to Arduino: {e}")
    arduino = None

def read_arduino_data():
    """Background thread to read data from Arduino"""
    while True:
        if arduino and arduino.in_waiting:
            try:
                data = arduino.readline().decode('utf-8').strip()
                if data:
                    sensor_data = json.loads(data)
                    car_state["sensor_data"].update(sensor_data)
            except:
                pass
        time.sleep(0.1)

def update_lidar_data():
    """Background thread to update LiDAR data"""
    while True:
        if lidar_processor:
            try:
                lidar_data = lidar_processor.get_obstacle_data()
                car_state["sensor_data"]["lidar"] = lidar_data
            except:
                pass
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify(car_state)

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    if 'mode' in data:
        car_state['mode'] = data['mode']
    if 'speed' in data:
        car_state['speed'] = data['speed']
    if 'steering' in data:
        car_state['steering'] = data['steering']
    
    # Send command to Arduino
    if arduino:
        command = json.dumps({
            'mode': car_state['mode'],
            'speed': car_state['speed'],
            'steering': car_state['steering']
        })
        arduino.write(command.encode())
    
    return jsonify({"status": "success"})

@app.route('/api/lidar', methods=['GET'])
def get_lidar_data():
    if lidar_processor:
        return jsonify(lidar_processor.get_scan_data())
    return jsonify({"error": "LiDAR not available"})

def cleanup():
    """Cleanup function to stop all threads and close connections"""
    if lidar_processor:
        lidar_processor.stop()
    if arduino:
        arduino.close()

if __name__ == '__main__':
    try:
        # Start Arduino communication thread
        arduino_thread = threading.Thread(target=read_arduino_data)
        arduino_thread.daemon = True
        arduino_thread.start()
        
        # Start LiDAR update thread
        lidar_thread = threading.Thread(target=update_lidar_data)
        lidar_thread.daemon = True
        lidar_thread.start()
        
        # Start Flask app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        cleanup()
    finally:
        cleanup() 