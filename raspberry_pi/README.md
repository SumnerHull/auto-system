# Autonomous System

A Raspberry Pi-based autonomous system with LiDAR navigation and web dashboard.

## Project Structure

```
raspberry_pi/
├── lidar_processing/     # LiDAR processing module
│   └── lidar_processor.py
├── web_dashboard/        # Web interface
│   ├── app.py
│   ├── static/
│   └── templates/
└── requirements.txt      # Python dependencies
```

## Hardware Requirements

1. **Raspberry Pi**
   - Model 3B+ or newer recommended
   - USB ports for LiDAR and Arduino connections

2. **RPLIDAR A1**
   - 5V power supply
   - USB to Serial converter (CP2102 or similar)

3. **Arduino Uno/Nano**
   - For motor control and sensors
   - USB connection to Raspberry Pi

## Software Requirements

- Python 3.7+
- pip (Python package manager)
- Required Python packages (see requirements.txt)

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Hardware Setup**
   - Connect LiDAR to Raspberry Pi via USB-Serial converter
   - Connect Arduino to Raspberry Pi via USB
   - Ensure all power connections are secure

3. **Run the System**
   ```bash
   python run_system.py
   ```

## Usage

1. **Web Dashboard**
   - Access at `http://localhost:5000`
   - View LiDAR data and system status
   - Control system parameters

2. **LiDAR Processing**
   - Automatic port detection
   - Real-time obstacle detection
   - Four-directional scanning

3. **Arduino Control**
   - Serial communication at 9600 baud
   - Motor control and sensor data

## Troubleshooting

1. **LiDAR Issues**
   - Check USB-Serial converter connection
   - Verify power supply (5V, 300mA)
   - Ensure correct baud rate (115200)

2. **Arduino Issues**
   - Verify USB connection
   - Check serial port settings
   - Ensure correct baud rate (9600)

3. **Web Dashboard Issues**
   - Check Flask server status
   - Verify port 5000 is available
   - Check network connectivity

## License

MIT License 