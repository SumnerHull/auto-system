#!/bin/bash

# Set up logging colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Auto-System Web Dashboard...${NC}"
echo "----------------------------------------"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed${NC}"
    exit 1
fi

# Check if required Python packages are installed
echo -e "${YELLOW}Checking Python dependencies...${NC}"
python3 -c "import flask, serial, threading, logging" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Required Python packages are missing${NC}"
    echo "Please install them using: pip3 install flask pyserial"
    exit 1
fi
echo -e "${GREEN}✓ All Python dependencies are installed${NC}"

# Check if COM4 is available
echo -e "${YELLOW}Checking Arduino connection...${NC}"
if [ -e /dev/ttyACM0 ]; then
    echo -e "${GREEN}✓ Arduino detected on /dev/ttyACM0${NC}"
elif [ -e /dev/ttyUSB0 ]; then
    echo -e "${GREEN}✓ Arduino detected on /dev/ttyUSB0${NC}"
else
    echo -e "${RED}Warning: No Arduino detected${NC}"
    echo "Please ensure Arduino is connected and try again"
fi

# Start the Flask application
echo -e "${YELLOW}Starting Flask web server...${NC}"
echo "----------------------------------------"
echo -e "${GREEN}Web Dashboard will be available at:${NC}"
echo -e "Local:    http://localhost:5000"
echo -e "Network:  http://$(hostname -I | awk '{print $1}'):5000"
echo "----------------------------------------"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo "----------------------------------------"

# Run the Flask application
python3 app.py

# Cleanup on exit
echo -e "${YELLOW}Shutting down...${NC}"
echo "----------------------------------------"
echo -e "${GREEN}Web Dashboard stopped${NC}" 