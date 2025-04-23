#include <Wire.h>
#include <MPU6050.h>  // Gyroscope library
#include <NewPing.h>  // Ultrasonic sensor library

// Motor control pins for Spark motor controllers
const int DRIVE_MOTOR_PWM = 5;    // PWM pin for drive motors
const int STEERING_MOTOR_PWM = 6;  // PWM pin for steering motor

// Ultrasonic sensor pins (45-degree angles at each corner)
const int TRIGGER_PIN_FRONT_LEFT = 2;
const int ECHO_PIN_FRONT_LEFT = 3;
const int TRIGGER_PIN_FRONT_RIGHT = 4;
const int ECHO_PIN_FRONT_RIGHT = 7;
const int TRIGGER_PIN_BACK_LEFT = 8;
const int ECHO_PIN_BACK_LEFT = 9;
const int TRIGGER_PIN_BACK_RIGHT = 10;
const int ECHO_PIN_BACK_RIGHT = 11;

// Battery monitoring
const int BATTERY_PIN = A0;  // Analog pin for battery voltage
const float VOLTAGE_DIVIDER_RATIO = 4.0;  // 15kΩ/5kΩ = 4.0 (safer for 12V)
const float REFERENCE_VOLTAGE = 5.0;  // Arduino reference voltage
const int ADC_RESOLUTION = 1023;  // 10-bit ADC

// Battery voltage thresholds for 12V battery
const float BATTERY_FULL_VOLTAGE = 12.7;  // Fully charged 12V battery
const float BATTERY_EMPTY_VOLTAGE = 10.5;  // Minimum safe voltage
const float BATTERY_WARNING_VOLTAGE = 11.0;  // Warning threshold

// Sensor objects
MPU6050 mpu;
NewPing sonarFrontLeft(TRIGGER_PIN_FRONT_LEFT, ECHO_PIN_FRONT_LEFT, 200);  // Max distance 200cm
NewPing sonarFrontRight(TRIGGER_PIN_FRONT_RIGHT, ECHO_PIN_FRONT_RIGHT, 200);
NewPing sonarBackLeft(TRIGGER_PIN_BACK_LEFT, ECHO_PIN_BACK_LEFT, 200);
NewPing sonarBackRight(TRIGGER_PIN_BACK_RIGHT, ECHO_PIN_BACK_RIGHT, 200);

// Global variables
String inputString = "";
bool stringComplete = false;
int currentSpeed = 0;
int currentSteering = 0;  // -100 to 100, where 0 is straight
String currentMode = "manual";
bool batteryWarning = false;
unsigned long lastLogTime = 0;
const unsigned long LOG_INTERVAL = 1000;  // Log every 1 second

void setup() {
    // Initialize serial communication
    Serial.begin(9600);
    inputString.reserve(200);

    // Initialize motor control pins
    pinMode(DRIVE_MOTOR_PWM, OUTPUT);
    pinMode(STEERING_MOTOR_PWM, OUTPUT);

    // Initialize MPU6050
    Wire.begin();
    mpu.initialize();
    if (!mpu.testConnection()) {
        sendLog("ERROR", "MPU6050 connection failed");
    } else {
        sendLog("INFO", "MPU6050 initialized successfully");
    }

    // Initialize battery monitoring
    pinMode(BATTERY_PIN, INPUT);
    analogReference(DEFAULT);  // Use 5V reference
    
    sendLog("INFO", "System initialized");
}

void loop() {
    // Read serial data if available
    if (stringComplete) {
        processCommand(inputString);
        inputString = "";
        stringComplete = false;
    }

    // Read sensor data
    int frontLeftDistance = sonarFrontLeft.ping_cm();
    int frontRightDistance = sonarFrontRight.ping_cm();
    int backLeftDistance = sonarBackLeft.ping_cm();
    int backRightDistance = sonarBackRight.ping_cm();
    
    int16_t ax, ay, az;
    int16_t gx, gy, gz;
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    // Check for obstacles and log warnings
    if (frontLeftDistance > 0 && frontLeftDistance < 30) {
        sendLog("WARNING", "Obstacle detected front left: " + String(frontLeftDistance) + "cm");
    }
    if (frontRightDistance > 0 && frontRightDistance < 30) {
        sendLog("WARNING", "Obstacle detected front right: " + String(frontRightDistance) + "cm");
    }
    if (backLeftDistance > 0 && backLeftDistance < 20) {
        sendLog("WARNING", "Obstacle detected back left: " + String(backLeftDistance) + "cm");
    }
    if (backRightDistance > 0 && backRightDistance < 20) {
        sendLog("WARNING", "Obstacle detected back right: " + String(backRightDistance) + "cm");
    }

    // Check battery level
    float batteryVoltage = getBatteryVoltage();
    if (batteryVoltage < BATTERY_WARNING_VOLTAGE && !batteryWarning) {
        batteryWarning = true;
        sendLog("WARNING", "Low battery: " + String(batteryVoltage) + "V");
    } else if (batteryVoltage >= BATTERY_WARNING_VOLTAGE) {
        batteryWarning = false;
    }

    // Send sensor data to Raspberry Pi
    String sensorData = "{\"ultrasonic\":{\"front_left\":" + String(frontLeftDistance) + 
                       ",\"front_right\":" + String(frontRightDistance) + 
                       ",\"back_left\":" + String(backLeftDistance) + 
                       ",\"back_right\":" + String(backRightDistance) + 
                       "},\"gyro\":{\"ax\":" + String(ax) + 
                       ",\"ay\":" + String(ay) + 
                       ",\"az\":" + String(az) + 
                       ",\"gx\":" + String(gx) + 
                       ",\"gy\":" + String(gy) + 
                       ",\"gz\":" + String(gz) + 
                       "},\"battery\":{\"voltage\":" + String(batteryVoltage) + 
                       ",\"warning\":" + String(batteryWarning) + "}}";
    Serial.println(sensorData);

    // Autonomous mode logic
    if (currentMode == "autonomous") {
        // Simple obstacle avoidance using all sensors
        if (frontLeftDistance > 0 && frontLeftDistance < 30 || 
            frontRightDistance > 0 && frontRightDistance < 30) {
            // Obstacle detected in front, turn based on which side has more space
            if (frontLeftDistance > frontRightDistance) {
                moveMotors(50, -50);  // Turn left
                sendLog("INFO", "Autonomous: Turning left to avoid obstacle");
            } else {
                moveMotors(50, 50);   // Turn right
                sendLog("INFO", "Autonomous: Turning right to avoid obstacle");
            }
        } else if (backLeftDistance > 0 && backLeftDistance < 20 || 
                  backRightDistance > 0 && backRightDistance < 20) {
            // Obstacle detected behind, move forward
            moveMotors(50, 0);
            sendLog("INFO", "Autonomous: Moving forward to avoid rear obstacle");
        } else {
            // No obstacles, move forward
            moveMotors(50, 0);
        }
    }

    // Periodic status logging
    unsigned long currentTime = millis();
    if (currentTime - lastLogTime >= LOG_INTERVAL) {
        lastLogTime = currentTime;
        sendLog("INFO", "Status: Mode=" + currentMode + 
                       " Speed=" + String(currentSpeed) + 
                       " Steering=" + String(currentSteering));
    }

    delay(100);  // Small delay to prevent overwhelming the serial buffer
}

void serialEvent() {
    while (Serial.available()) {
        char inChar = (char)Serial.read();
        inputString += inChar;
        if (inChar == '\n') {
            stringComplete = true;
        }
    }
}

void processCommand(String command) {
    // Parse JSON command
    // Example command: {"mode":"manual","speed":50,"steering":0}
    int modeStart = command.indexOf("\"mode\":\"") + 8;
    int modeEnd = command.indexOf("\"", modeStart);
    String newMode = command.substring(modeStart, modeEnd);
    
    if (newMode != currentMode) {
        currentMode = newMode;
        sendLog("INFO", "Mode changed to: " + currentMode);
    }

    int speedStart = command.indexOf("\"speed\":") + 8;
    int speedEnd = command.indexOf(",", speedStart);
    if (speedEnd == -1) speedEnd = command.indexOf("}", speedStart);
    int newSpeed = command.substring(speedStart, speedEnd).toInt();
    
    if (newSpeed != currentSpeed) {
        currentSpeed = newSpeed;
        sendLog("INFO", "Speed changed to: " + String(currentSpeed));
    }

    int steeringStart = command.indexOf("\"steering\":") + 11;
    int steeringEnd = command.indexOf("}", steeringStart);
    int newSteering = command.substring(steeringStart, steeringEnd).toInt();
    
    if (newSteering != currentSteering) {
        currentSteering = newSteering;
        sendLog("INFO", "Steering changed to: " + String(currentSteering));
    }
}

void moveMotors(int speed, int steering) {
    // Convert speed and steering percentages to PWM values (0-255)
    int drivePWM = map(abs(speed), 0, 100, 0, 255);
    int steeringPWM = map(abs(steering), 0, 100, 0, 255);
    
    // Set drive motor direction and speed
    if (speed > 0) {
        // Forward
        analogWrite(DRIVE_MOTOR_PWM, drivePWM);
    } else if (speed < 0) {
        // Reverse
        analogWrite(DRIVE_MOTOR_PWM, drivePWM);
    } else {
        // Stop
        analogWrite(DRIVE_MOTOR_PWM, 0);
    }
    
    // Set steering motor direction and speed
    if (steering > 0) {
        // Turn right
        analogWrite(STEERING_MOTOR_PWM, steeringPWM);
    } else if (steering < 0) {
        // Turn left
        analogWrite(STEERING_MOTOR_PWM, steeringPWM);
    } else {
        // Center
        analogWrite(STEERING_MOTOR_PWM, 0);
    }
}

float getBatteryVoltage() {
    // Read analog value and convert to voltage
    int rawValue = analogRead(BATTERY_PIN);
    float voltage = (rawValue * REFERENCE_VOLTAGE / ADC_RESOLUTION) * VOLTAGE_DIVIDER_RATIO;
    return voltage;
}

void sendLog(String level, String message) {
    String logMessage = "{\"log\":{\"level\":\"" + level + 
                       "\",\"message\":\"" + message + 
                       "\",\"timestamp\":" + String(millis()) + "}}";
    Serial.println(logMessage);
} 