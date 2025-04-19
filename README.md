# Autonomous Power Wheels Car

This project transforms a Power Wheels car into an autonomous vehicle using a Raspberry Pi and Arduino.

## System Architecture

### Hardware Components
- Raspberry Pi (Main Controller)
  - LiDAR sensor
  - Web dashboard
  - Communication with Arduino
- Arduino (Motor Controller)
  - Motor control via PWM
  - Gyroscope sensor
  - Ultrasonic sensors
  - Communication with Raspberry Pi

### Software Components
- Web Dashboard (Raspberry Pi)
  - Real-time monitoring
  - Mode selection
  - Manual control interface
- Arduino Firmware
  - Motor control
  - Sensor data collection
  - Communication protocol

## Project Structure
```
.
├── README.md
├── raspberry_pi/
│   ├── web_dashboard/
│   ├── lidar_processing/
│   └── arduino_communication/
└── arduino/
    ├── motor_control/
    ├── sensor_processing/
    └── communication/
```

## Setup Instructions
(To be added as development progresses)

## Safety Considerations
- Always test in a controlled environment
- Implement emergency stop functionality
- Monitor battery levels
- Keep manual override capability 