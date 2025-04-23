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

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        echo "Please install venv: sudo apt-get install python3-venv"
        exit 1
    fi
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install required packages
echo -e "${YELLOW}Installing/updating Python dependencies...${NC}"
pip install --upgrade pip
pip install flask pyserial rplidar-roboticia
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install required packages${NC}"
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
python app.py

# Cleanup on exit
echo -e "${YELLOW}Shutting down...${NC}"
echo "----------------------------------------"
echo -e "${GREEN}Web Dashboard stopped${NC}"
deactivate 