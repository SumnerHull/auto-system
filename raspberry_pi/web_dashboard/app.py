from flask import Flask, render_template, jsonify, request
import json
import serial
import threading
import time
import sys
import os
import logging
from datetime import datetime
from flask_socketio import SocketIO, emit

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lidar_processing.lidar_processor import LidarProcessor

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('web_dashboard')

def reset_serial_port(port):
    """Reset the serial port by closing it if it's open"""
    try:
        # Try to open the port to check if it's already open
        test_serial = serial.Serial(port)
        test_serial.close()
        logger.info(f"Successfully reset port {port}")
    except serial.SerialException as e:
        logger.info(f"Port {port} was not open or already closed")
    except Exception as e:
        logger.error(f"Error resetting port {port}: {e}")

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
        "lidar": {},
        "battery": {
            "voltage": 0.0,
            "warning": False
        }
    }
}

# Initialize LiDAR processor
lidar_processor = None
try:
    lidar_processor = LidarProcessor(port='/dev/ttyUSB0')
    lidar_processor.start()
    logger.info("LiDAR initialized")
except Exception as e:
    logger.error(f"Could not initialize LiDAR: {e}")

# Serial communication with Arduino
try:
    # Reset the COM port before opening it
    reset_serial_port('/dev/ttyACM0')
    arduino = serial.Serial(
        port='/dev/ttyACM0',
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1,
        write_timeout=1,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False
    )
    # Flush any existing data
    arduino.reset_input_buffer()
    arduino.reset_output_buffer()
    # Enable DTR and RTS
    arduino.dtr = True
    arduino.rts = True
    time.sleep(2)  # Give the Arduino time to reset
    logger.info("Arduino connected and configured")
except Exception as e:
    logger.error(f"Could not connect to Arduino: {e}")
    arduino = None

def read_arduino_data():
    """Background thread to read data from Arduino"""
    while True:
        if arduino and arduino.in_waiting:
            try:
                data = arduino.readline().decode('utf-8').strip()
                if data:
                    logger.debug(f"Received from Arduino: {data}")
                    try:
                        # Check if this is a log message
                        if data.startswith('{"log":'):
                            log_data = json.loads(data)["log"]
                            logger.info(f"Arduino {log_data['level']}: {log_data['message']}")
                            socketio.emit('log', {
                                'message': log_data['message'],
                                'type': log_data['level']
                            })
                        else:
                            # Regular sensor data
                            sensor_data = json.loads(data)
                            car_state["sensor_data"].update(sensor_data)
                            # Emit sensor data update
                            socketio.emit('sensor_update', sensor_data)
                            logger.debug(f"Updated sensor data: {sensor_data}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing Arduino data: {e}")
            except Exception as e:
                logger.error(f"Error reading from Arduino: {e}")
        time.sleep(0.1)

def update_lidar_data():
    """Background thread to update LiDAR data"""
    while True:
        if lidar_processor:
            try:
                lidar_data = lidar_processor.get_obstacle_data()
                car_state["sensor_data"]["lidar"] = lidar_data
                # Emit LiDAR data update
                socketio.emit('lidar_update', lidar_data)
            except Exception as e:
                logger.error(f"Error updating LiDAR data: {e}")
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state')
def get_state():
    return jsonify(car_state)

@app.route('/api/control', methods=['POST'])
def control():
    try:
        data = request.json
        if 'mode' in data:
            car_state['mode'] = data['mode']
            logger.info(f"Mode changed to: {data['mode']}")
            socketio.emit('mode_update', {'mode': data['mode']})
        if 'speed' in data:
            car_state['speed'] = data['speed']
            logger.info(f"Speed changed to: {data['speed']}")
            socketio.emit('speed_update', {'speed': data['speed']})
        if 'steering' in data:
            car_state['steering'] = data['steering']
            logger.info(f"Steering changed to: {data['steering']}")
            socketio.emit('steering_update', {'steering': data['steering']})
        
        # Send command to Arduino
        if arduino:
            command = json.dumps(car_state)
            logger.debug(f"Sending to Arduino: {command}")
            arduino.write((command + '\n').encode())
            arduino.flush()  # Ensure data is sent
            logger.debug("Command sent and flushed")
        
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error processing control command: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/lidar', methods=['GET'])
def get_lidar_data():
    if lidar_processor:
        return jsonify(lidar_processor.get_scan_data())
    return jsonify({"error": "LiDAR not available"})

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    # Send initial state
    emit('initial_state', car_state)

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

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
        
        # Start Flask app with SocketIO
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        cleanup()
    finally:
        cleanup() 