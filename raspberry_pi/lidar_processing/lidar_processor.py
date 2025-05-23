from rplidar import RPLidar
import time
import json
import serial.tools.list_ports
import serial
import logging

class LidarProcessor:
    def __init__(self, port=None):
        """Initialize LiDAR processor with optional port parameter"""
        self.port = port
        self.lidar = None
        self.scanning = False
        self.obstacle_data = {
            "front": 0,
            "left": 0,
            "right": 0,
            "back": 0
        }
        
        # Set up logging
        self.logger = logging.getLogger('lidar_processor')
        self.logger.setLevel(logging.INFO)
        
        # Print available ports
        self.logger.info("\nAvailable serial ports:")
        for port in serial.tools.list_ports.comports():
            self.logger.info(f"- {port.device}")

    def find_lidar_port(self):
        """Try to automatically detect the LiDAR port"""
        self.logger.info("\nAttempting to detect LiDAR port...")
        
        # Try all available ports
        for port in serial.tools.list_ports.comports():
            if self.try_port(port.device):
                return port.device
        
        self.logger.error("Could not detect LiDAR port")
        return None

    def try_port(self, port):
        """Try to connect to a specific port and verify it's a LiDAR"""
        self.logger.info(f"Trying port {port}...")
        
        try:
            # Try to initialize LiDAR
            lidar = RPLidar(port)
            
            # Try to get device info
            info = lidar.get_info()
            lidar.disconnect()
            
            self.logger.info(f"✓ Found LiDAR on port {port}")
            self.logger.info(f"LiDAR Info: {info}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error testing port {port}: {str(e)}")
            return False

    def start(self):
        """Start LiDAR scanning"""
        try:
            # If no port specified, try to detect it
            if self.port is None:
                self.port = self.find_lidar_port()
                if self.port is None:
                    self.logger.error("Error: Could not find LiDAR port")
                    return False
            
            self.logger.info(f"\nConnecting to LiDAR on port {self.port}")
            
            # Initialize LiDAR
            self.lidar = RPLidar(self.port)
            self.scanning = True
            
            # Test connection
            info = self.lidar.get_info()
            self.logger.info(f"✓ LiDAR connected successfully")
            self.logger.info(f"LiDAR Info: {info}")
            
            # Check health status
            health_status, error_code = self.lidar.get_health()
            if health_status != "Good":
                self.logger.warning(f"LiDAR health status: {health_status} (Error code: {error_code})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting LiDAR: {str(e)}")
            return False

    def stop(self):
        """Stop LiDAR scanning"""
        if self.lidar:
            try:
                self.scanning = False
                self.lidar.stop()
                self.lidar.disconnect()
                self.logger.info("✓ LiDAR stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping LiDAR: {str(e)}")

    def get_scan_data(self):
        """Get raw scan data"""
        if not self.scanning or not self.lidar:
            self.logger.warning("LiDAR not initialized")
            return {"error": "LiDAR not initialized"}

        try:
            scan_data = []
            for scan in self.lidar.iter_scans():
                scan_data.append(scan)
                if len(scan_data) >= 1:  # Get one scan
                    break
            return scan_data
        except Exception as e:
            self.logger.error(f"Error getting scan data: {str(e)}")
            return {"error": str(e)}

    def get_obstacle_data(self):
        """Process scan data to detect obstacles"""
        if not self.scanning or not self.lidar:
            self.logger.warning("LiDAR not initialized")
            return self.obstacle_data

        try:
            scan = next(self.lidar.iter_scans())
            front_dist = float('inf')
            left_dist = float('inf')
            right_dist = float('inf')
            back_dist = float('inf')

            for (_, angle, distance) in scan:
                # Convert angle to 0-360 range
                angle = angle % 360
                
                # Front (0 degrees)
                if 0 <= angle <= 45 or 315 <= angle <= 360:
                    front_dist = min(front_dist, distance)
                # Right (90 degrees)
                elif 45 <= angle <= 135:
                    right_dist = min(right_dist, distance)
                # Back (180 degrees)
                elif 135 <= angle <= 225:
                    back_dist = min(back_dist, distance)
                # Left (270 degrees)
                elif 225 <= angle <= 315:
                    left_dist = min(left_dist, distance)

            self.obstacle_data = {
                "front": front_dist if front_dist != float('inf') else 0,
                "left": left_dist if left_dist != float('inf') else 0,
                "right": right_dist if right_dist != float('inf') else 0,
                "back": back_dist if back_dist != float('inf') else 0
            }
            
            # Log obstacle detection
            for direction, distance in self.obstacle_data.items():
                if distance > 0 and distance < 100:  # Obstacle within 100mm
                    self.logger.warning(f"Obstacle detected {direction}: {distance}mm")
            
            return self.obstacle_data
        except Exception as e:
            self.logger.error(f"Error processing LiDAR data: {str(e)}")
            return self.obstacle_data

if __name__ == "__main__":
    # Test the LiDAR processor
    processor = LidarProcessor()
    try:
        if processor.start():
            while True:
                data = processor.get_obstacle_data()
                print(json.dumps(data, indent=2))
                time.sleep(0.1)
    except KeyboardInterrupt:
        processor.stop()