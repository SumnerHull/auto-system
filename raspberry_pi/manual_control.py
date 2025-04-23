import serial
import time
import json
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('manual_control')

def reset_serial_port(port):
    """Reset the serial port by closing it if it's open"""
    try:
        test_serial = serial.Serial(port)
        test_serial.close()
        logger.info(f"Successfully reset port {port}")
    except serial.SerialException as e:
        logger.info(f"Port {port} was not open or already closed")
    except Exception as e:
        logger.error(f"Error resetting port {port}: {e}")

def connect_to_arduino():
    """Connect to Arduino and return the serial connection"""
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
            dsrdtr=False,
            inter_byte_timeout=0.1
        )
        # Flush any existing data
        arduino.reset_input_buffer()
        arduino.reset_output_buffer()
        # Enable DTR and RTS
        arduino.dtr = True
        arduino.rts = True
        time.sleep(2)  # Give the Arduino time to reset
        logger.info("Arduino connected and configured")
        return arduino
    except Exception as e:
        logger.error(f"Could not connect to Arduino: {e}")
        return None

def send_command(arduino, command):
    """Send a command to the Arduino"""
    try:
        command_str = json.dumps(command) + '\n'
        arduino.write(command_str.encode())
        arduino.flush()
        logger.info(f"Sent command: {command}")
    except Exception as e:
        logger.error(f"Error sending command: {e}")

def print_help():
    """Print help message"""
    print("\nManual Control Commands:")
    print("  w - Move forward")
    print("  s - Move backward")
    print("  a - Turn left")
    print("  d - Turn right")
    print("  space - Stop")
    print("  m - Toggle manual/autonomous mode")
    print("  e - Emergency stop")
    print("  q - Quit")
    print("  h - Show this help message")

def main():
    # Initialize car state
    car_state = {
        "mode": "manual",
        "speed": 0,
        "steering": 0
    }

    # Connect to Arduino
    arduino = connect_to_arduino()
    if not arduino:
        logger.error("Failed to connect to Arduino. Exiting.")
        return

    print("\nAuto-System Manual Control")
    print("==========================")
    print_help()

    try:
        while True:
            # Get user input
            cmd = input("\nEnter command: ").lower()

            if cmd == 'q':
                break
            elif cmd == 'h':
                print_help()
            elif cmd == 'w':
                car_state['speed'] = 50
                send_command(arduino, car_state)
            elif cmd == 's':
                car_state['speed'] = -50
                send_command(arduino, car_state)
            elif cmd == 'a':
                car_state['steering'] = -50
                send_command(arduino, car_state)
            elif cmd == 'd':
                car_state['steering'] = 50
                send_command(arduino, car_state)
            elif cmd == ' ':
                car_state['speed'] = 0
                car_state['steering'] = 0
                send_command(arduino, car_state)
            elif cmd == 'm':
                car_state['mode'] = 'autonomous' if car_state['mode'] == 'manual' else 'manual'
                send_command(arduino, car_state)
                print(f"Mode changed to: {car_state['mode']}")
            elif cmd == 'e':
                car_state['mode'] = 'emergency'
                car_state['speed'] = 0
                car_state['steering'] = 0
                send_command(arduino, car_state)
                print("Emergency stop activated!")
            else:
                print("Invalid command. Type 'h' for help.")

            # Read any response from Arduino
            if arduino.in_waiting > 0:
                try:
                    response = arduino.readline().decode('utf-8', errors='replace').strip()
                    if response:
                        print(f"Arduino: {response}")
                except Exception as e:
                    logger.error(f"Error reading Arduino response: {e}")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Clean up
        if arduino:
            arduino.close()
        print("Connection closed.")

if __name__ == '__main__':
    main() 