# RPLIDAR A1 Wiring Diagram

## Components Required
- RPLIDAR A1
- Raspberry Pi
- USB to Serial Converter (CP2102 or similar)
- Jumper wires
- 5V power supply (if not using USB power)

## Connection Diagram

```
RPLIDAR A1 Pinout:
+------------------+
|                  |
| 1: GND           |
| 2: 5V            |
| 3: MOTOCTL       |
| 4: RX            |
| 5: TX            |
|                  |
+------------------+

USB to Serial Converter Pinout:
+------------------+
|                  |
| GND  <--->  GND  |
| 5V   <--->  5V   |
| TX   <--->  RX   |
| RX   <--->  TX   |
|                  |
+------------------+

Raspberry Pi USB Port:
+------------------+
|                  |
| Connect USB to   |
| Serial Converter |
|                  |
+------------------+
```

## Connection Instructions

1. **Power Connections:**
   - Connect RPLIDAR GND to USB-Serial GND
   - Connect RPLIDAR 5V to USB-Serial 5V
   - If using external power supply:
     - Connect 5V power supply positive to RPLIDAR 5V
     - Connect 5V power supply negative to RPLIDAR GND

2. **Data Connections:**
   - Connect RPLIDAR RX to USB-Serial TX
   - Connect RPLIDAR TX to USB-Serial RX
   - Connect RPLIDAR MOTOCTL to USB-Serial 5V (for motor control)

3. **USB Connection:**
   - Connect USB-Serial converter to Raspberry Pi USB port

## Important Notes

1. **Power Requirements:**
   - RPLIDAR A1 requires 5V power
   - Current draw: ~300mA during operation
   - Ensure power supply can provide sufficient current

2. **Serial Communication:**
   - Baud rate: 115200
   - Data bits: 8
   - Stop bits: 1
   - Parity: None
   - Flow control: None

3. **Safety Precautions:**
   - Double-check all connections before powering on
   - Ensure correct voltage (5V only)
   - Do not reverse polarity
   - Keep connections secure and insulated

4. **Testing:**
   - After connections are made:
     1. Power on the system
     2. Check if the LiDAR motor spins up
     3. Verify serial port appears in device list
     4. Run test script to confirm communication

## Troubleshooting

1. **LiDAR not spinning:**
   - Check MOTOCTL connection
   - Verify power supply voltage
   - Check for loose connections

2. **No serial communication:**
   - Verify RX/TX connections are not reversed
   - Check USB-Serial converter is recognized
   - Verify correct baud rate settings

3. **Power issues:**
   - Check voltage at RPLIDAR power pins
   - Verify ground connections
   - Ensure power supply can handle current draw 