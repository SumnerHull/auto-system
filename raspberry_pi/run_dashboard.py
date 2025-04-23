import sys
import os
from web_dashboard.app import app

def main():
    try:
        print("Starting web dashboard...")
        print("Access the dashboard at: http://localhost:5000")
        print("Press Ctrl+C to stop")
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nStopping web dashboard...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting web dashboard: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 