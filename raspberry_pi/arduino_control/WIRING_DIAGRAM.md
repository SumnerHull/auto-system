# Arduino Wiring Diagram

## Components Required
- Arduino Uno/Nano
- Raspberry Pi
- USB Cable (Type A to Type B for Uno, Micro USB for Nano)
- Jumper wires
- 5V power supply (if not using USB power)

## Connection Diagram

```
Arduino Pinout:
+------------------+
|                  |
| 5V  <--->  5V   |
| GND <--->  GND  |
| RX  <--->  TX   |
| TX  <--->  RX   |
|                  |
+------------------+

Raspberry Pi USB Port:
+------------------+
|                  |
| Connect USB to   |
| Arduino          |
|                  |
+------------------+
```

## Connection Instructions

1. **USB Connection:**
   - Connect Arduino to Raspberry Pi using USB cable
   - This provides both power and serial communication

2. **Alternative Power Connection (if not using USB):**
   - Connect Arduino 5V to power supply positive
   - Connect Arduino GND to power supply negative
   - Ensure power supply provides 5V DC

## Serial Communication Setup

1. **Baud Rate:**
   - Set to 9600 in Arduino code
   - Match this in Raspberry Pi code

2. **Serial Port:**
   - On Raspberry Pi: `/dev/ttyACM0` (typical for Arduino)
   - On Windows: `COM3` or similar (check Device Manager)

## Important Notes

1. **Power Requirements:**
   - Arduino operates at 5V
   - USB provides sufficient power for most applications
   - If using external power:
     - Voltage: 5V DC
     - Current: ~500mA recommended
     - Do not exceed 12V input

2. **Serial Communication:**
   - Baud rate: 9600 (default for Arduino)
   - Data bits: 8
   - Stop bits: 1
   - Parity: None
   - Flow control: None

3. **Safety Precautions:**
   - Double-check all connections before powering on
   - Ensure correct voltage (5V only for direct connection)
   - Do not reverse polarity
   - Keep connections secure and insulated

4. **Testing:**
   - After connections are made:
     1. Power on the system
     2. Check if Arduino LED blinks (indicates power)
     3. Verify serial port appears in device list
     4. Run test script to confirm communication

## Troubleshooting

1. **Arduino not recognized:**
   - Check USB cable connection
   - Try different USB port
   - Verify Arduino drivers are installed
   - Check Device Manager for correct COM port

2. **No serial communication:**
   - Verify baud rate matches in both Arduino and Raspberry Pi code
   - Check if correct serial port is selected
   - Ensure no other program is using the serial port

3. **Power issues:**
   - Check USB cable quality
   - Verify power supply voltage if using external power
   - Check for loose connections

## Example Arduino Code Structure

```cpp
void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Setup pins and initial state
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // Check for incoming serial data
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    
    // Process command
    if (command == "ON") {
      digitalWrite(LED_BUILTIN, HIGH);
    } else if (command == "OFF") {
      digitalWrite(LED_BUILTIN, LOW);
    }
    
    // Send acknowledgment
    Serial.println("ACK");
  }
}
``` 