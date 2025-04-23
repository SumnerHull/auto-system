import serial
import time
import sys
import os
from typing import Optional

class MotorTester:
    def __init__(self, port: str = "COM3", baudrate: int = 9600):
        """Initialize the motor tester with serial port settings."""
        self.port = port
        self.baudrate = baudrate
        self.serial_connection: Optional[serial.Serial] = None

    def connect(self) -> bool:
        """Connect to the Arduino via serial port."""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False

    def disconnect(self):
        """Close the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Disconnected from serial port")

    def send_command(self, command: str) -> bool:
        """Send a command to the Arduino."""
        if not self.serial_connection or not self.serial_connection.is_open:
            print("Not connected to serial port")
            return False

        try:
            self.serial_connection.write(f"{command}\n".encode())
            return True
        except serial.SerialException as e:
            print(f"Error sending command: {e}")
            return False

    def test_motor(self, speed: int, duration: float = 1.0):
        """Test a motor with specified speed and duration."""
        if not -100 <= speed <= 100:
            print("Speed must be between -100 and 100")
            return

        command = f"MOTOR {speed}"
        print(f"Testing motor at {speed}% speed for {duration} seconds")
        
        if self.send_command(command):
            time.sleep(duration)
            self.send_command("MOTOR 0")  # Stop motor
            print("Motor test completed")

    def test_steering(self, angle: int, duration: float = 1.0):
        """Test steering with specified angle and duration."""
        if not -100 <= angle <= 100:
            print("Angle must be between -100 and 100")
            return

        command = f"STEER {angle}"
        print(f"Testing steering at {angle}% angle for {duration} seconds")
        
        if self.send_command(command):
            time.sleep(duration)
            self.send_command("STEER 0")  # Center steering
            print("Steering test completed")

def list_serial_ports():
    """List all available serial ports on Windows."""
    import winreg
    ports = []
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
        i = 0
        while True:
            try:
                ports.append(winreg.EnumValue(key, i)[1])
                i += 1
            except WindowsError:
                break
    except WindowsError:
        pass
    return ports

def main():
    # List available ports
    print("Available serial ports:")
    ports = list_serial_ports()
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port}")

    # Get port selection
    while True:
        try:
            selection = input("\nEnter the number of the port to use (or 'q' to quit): ")
            if selection.lower() == 'q':
                return
            port_index = int(selection) - 1
            if 0 <= port_index < len(ports):
                break
            print("Invalid selection")
        except ValueError:
            print("Please enter a valid number")

    # Initialize motor tester
    tester = MotorTester(port=ports[port_index])
    if not tester.connect():
        return

    try:
        while True:
            print("\nMotor Test Menu:")
            print("1. Test Motor Speed")
            print("2. Test Steering")
            print("3. Exit")
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == '1':
                try:
                    speed = int(input("Enter speed (-100 to 100): "))
                    duration = float(input("Enter duration in seconds: "))
                    tester.test_motor(speed, duration)
                except ValueError:
                    print("Invalid input. Please enter numbers only.")
            
            elif choice == '2':
                try:
                    angle = int(input("Enter angle (-100 to 100): "))
                    duration = float(input("Enter duration in seconds: "))
                    tester.test_steering(angle, duration)
                except ValueError:
                    print("Invalid input. Please enter numbers only.")
            
            elif choice == '3':
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    finally:
        tester.disconnect()

if __name__ == "__main__":
    main() 