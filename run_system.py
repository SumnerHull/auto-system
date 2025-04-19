import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path
import platform
import ctypes
import shutil
import pkg_resources

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Relaunch the script with administrator privileges"""
    if platform.system() == 'Windows' and not is_admin():
        print("Requesting administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def get_system_python():
    """Get the path to the system Python executable"""
    if platform.system() == 'Windows':
        # Try to find Python in common installation locations
        username = os.getenv('USERNAME')
        possible_paths = [
            # User-specific installations
            f"C:\\Users\\{username}\\AppData\\Local\\Programs\\Python\\Python39\\python.exe",
            f"C:\\Users\\{username}\\AppData\\Local\\Programs\\Python\\Python310\\python.exe",
            f"C:\\Users\\{username}\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
            # System-wide installations
            r"C:\Python39\python.exe",
            r"C:\Python310\python.exe",
            r"C:\Python311\python.exe",
            # Program Files installations
            r"C:\Program Files\Python39\python.exe",
            r"C:\Program Files\Python310\python.exe",
            r"C:\Program Files\Python311\python.exe",
            r"C:\Program Files (x86)\Python39\python.exe",
            r"C:\Program Files (x86)\Python310\python.exe",
            r"C:\Program Files (x86)\Python311\python.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found Python at: {path}")
                return path
        
        # If not found in common locations, try to find it in PATH
        python_path = shutil.which('python')
        if python_path:
            print(f"Found Python in PATH at: {python_path}")
            return python_path
            
        raise Exception("Could not find system Python installation")
    else:
        return shutil.which('python3') or shutil.which('python')

def ensure_pip_installed(python_path):
    """Ensure pip is installed for the given Python installation"""
    print("\nChecking pip installation...")
    
    # Try multiple possible pip locations
    possible_pip_paths = [
        str(Path(python_path).parent / "pip.exe"),  # Same directory as python.exe
        str(Path(python_path).parent.parent / "Scripts" / "pip.exe"),  # Python39/Scripts
        str(Path(python_path).parent.parent / "Scripts" / "pip3.exe"),  # Python39/Scripts
        f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\Programs\\Python\\Python39\\Scripts\\pip.exe",
        f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\Programs\\Python\\Python310\\Scripts\\pip.exe",
        f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe",
    ]
    
    for pip_path in possible_pip_paths:
        if os.path.exists(pip_path):
            print(f"Found pip at: {pip_path}")
            return pip_path
    
    print("Pip not found in any standard location. Attempting to install pip...")
    try:
        # Download get-pip.py
        print("Downloading get-pip.py...")
        import urllib.request
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", "get-pip.py")
        
        # Run get-pip.py
        print("Installing pip...")
        result = subprocess.run(
            [str(python_path), "get-pip.py"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        # Clean up
        os.remove("get-pip.py")
        
        # Check all possible locations again
        for pip_path in possible_pip_paths:
            if os.path.exists(pip_path):
                print(f"Found pip at: {pip_path}")
                return pip_path
        
        raise Exception("Pip installation failed - could not find pip after installation")
        
    except Exception as e:
        print(f"Error installing pip: {e}")
        print("\nPlease install pip manually by following these steps:")
        print("1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py")
        print("2. Open a command prompt as administrator")
        print(f"3. Run: {python_path} get-pip.py")
        print("\nAfter installing pip, run this script again.")
        sys.exit(1)

def check_python_version():
    """Check if Python version is compatible"""
    print(f"Current Python version: {sys.version}")
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    print("✓ Python version is compatible")

def create_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True, capture_output=True, text=True)
            print("✓ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e.stderr}")
            sys.exit(1)
    else:
        print("✓ Virtual environment already exists")

def get_script_directory():
    """Get the directory where this script is located"""
    if getattr(sys, 'frozen', False):
        # If the script is running as a compiled executable
        return os.path.dirname(sys.executable)
    else:
        # If the script is running as a Python file
        return os.path.dirname(os.path.abspath(__file__))

def install_requirements(use_venv=True):
    """Install required packages"""
    print("\n=== Starting Requirements Installation ===")
    print(f"Using {'virtual environment' if use_venv else 'system Python'}")
    
    # Get the script's directory
    script_dir = get_script_directory()
    requirements_path = os.path.join(script_dir, "raspberry_pi", "requirements.txt")
    
    if not os.path.exists(requirements_path):
        print(f"Error: requirements.txt not found at {requirements_path}")
        sys.exit(1)
    
    try:
        if use_venv:
            print("\nChecking virtual environment...")
            pip_path = Path("venv/Scripts/pip.exe")
            if not pip_path.exists():
                print("Error: pip not found in virtual environment")
                print("Please make sure the virtual environment was created successfully")
                sys.exit(1)
            python_path = Path("venv/Scripts/python.exe")
            print(f"Using virtual environment Python at: {python_path}")
        else:
            print("\nLooking for system Python...")
            try:
                python_path = get_system_python()
                print(f"Found system Python at: {python_path}")
                
                # Ensure pip is installed
                pip_path = ensure_pip_installed(python_path)
                print(f"Using pip at: {pip_path}")
                
            except Exception as e:
                print(f"Error finding system Python: {e}")
                print("Full error details:")
                import traceback
                traceback.print_exc()
                sys.exit(1)
        
        # First, upgrade pip
        print("\nUpgrading pip...")
        try:
            subprocess.run(
                [str(pip_path), "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
                text=True
            )
            print("✓ Pip upgraded successfully")
        except Exception as e:
            print(f"Warning: Failed to upgrade pip: {e}")
            print("Continuing with installation anyway...")
        
        # Install requirements
        print("\nInstalling requirements...")
        try:
            result = subprocess.run(
                [str(pip_path), "install", "-r", requirements_path],
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            print("✓ Requirements installed successfully")
        except Exception as e:
            print(f"Error installing requirements: {e}")
            sys.exit(1)
        
    except Exception as e:
        print("\n=== Installation Failed ===")
        print(f"Error during installation: {str(e)}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        print("\nPlease check your Python installation and try again")
        sys.exit(1)

def start_processes(use_venv=True):
    """Start all system processes in separate terminals with admin privileges"""
    # Get the script's directory
    script_dir = get_script_directory()
    print(f"\nRunning from directory: {script_dir}")
    
    if use_venv:
        python_path = Path("venv/Scripts/python.exe")
        if not python_path.exists():
            print("Error: Python not found in virtual environment")
            sys.exit(1)
    else:
        try:
            python_path = get_system_python()
            print(f"Using system Python at: {python_path}")
        except Exception as e:
            print(f"Error finding system Python: {e}")
            sys.exit(1)

    try:
        # Start Flask server with admin privileges
        print("\nStarting Flask server...")
        flask_script = os.path.join(script_dir, "raspberry_pi", "web_dashboard", "app.py")
        if not os.path.exists(flask_script):
            print(f"Error: Flask script not found at {flask_script}")
            sys.exit(1)
            
        flask_cmd = f'"{python_path}" "{flask_script}"'
        
        if platform.system() == 'Windows':
            try:
                # Try to start with admin privileges
                print("Attempting to start Flask server with admin privileges...")
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,  # hwnd
                    "runas",  # operation
                    "cmd.exe",  # file
                    f'/k cd /d "{script_dir}" && {flask_cmd}',  # parameters
                    None,  # directory
                    1  # show command
                )
                
                if result <= 32:  # ShellExecute returns values <= 32 on error
                    print("Failed to start with admin privileges. Trying without...")
                    # Try without admin privileges
                    subprocess.Popen(
                        f'start cmd /k cd /d "{script_dir}" && {flask_cmd}',
                        shell=True
                    )
            except Exception as e:
                print(f"Error starting Flask server: {e}")
                print("Trying alternative method...")
                # Try alternative method
                subprocess.Popen(
                    f'start cmd /k cd /d "{script_dir}" && {flask_cmd}',
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
        else:
            subprocess.Popen(
                f'cd "{script_dir}" && {flask_cmd}',
                shell=True
            )
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Open the web browser
        webbrowser.open("http://localhost:5000")
        
        # Start LiDAR processor with admin privileges
        print("\nStarting LiDAR processor...")
        lidar_script = os.path.join(script_dir, "raspberry_pi", "lidar_processing", "lidar_processor.py")
        if not os.path.exists(lidar_script):
            print(f"Error: LiDAR script not found at {lidar_script}")
            sys.exit(1)
            
        lidar_cmd = f'"{python_path}" "{lidar_script}"'
        
        if platform.system() == 'Windows':
            try:
                # Try to start with admin privileges
                print("Attempting to start LiDAR processor with admin privileges...")
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,  # hwnd
                    "runas",  # operation
                    "cmd.exe",  # file
                    f'/k cd /d "{script_dir}" && {lidar_cmd}',  # parameters
                    None,  # directory
                    1  # show command
                )
                
                if result <= 32:  # ShellExecute returns values <= 32 on error
                    print("Failed to start with admin privileges. Trying without...")
                    # Try without admin privileges
                    subprocess.Popen(
                        f'start cmd /k cd /d "{script_dir}" && {lidar_cmd}',
                        shell=True
                    )
            except Exception as e:
                print(f"Error starting LiDAR processor: {e}")
                print("Trying alternative method...")
                # Try alternative method
                subprocess.Popen(
                    f'start cmd /k cd /d "{script_dir}" && {lidar_cmd}',
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
        else:
            subprocess.Popen(
                f'cd "{script_dir}" && {lidar_cmd}',
                shell=True
            )
        
        print("\nAll processes started in separate windows.")
        print("You can monitor each process in its own terminal window.")
        print("Press Ctrl+C in any terminal to stop that process.")
        print("To stop all processes, close all terminal windows.")
        
    except Exception as e:
        print(f"Error starting processes: {str(e)}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        print("\nIf you're seeing permission errors, try:")
        print("1. Running this script as administrator")
        print("2. Checking if your antivirus is blocking the processes")
        print("3. Making sure the Python scripts have read/execute permissions")
        sys.exit(1)

def main():
    try:
        # Basic system checks
        print("\n=== System Check ===")
        print(f"Operating System: {platform.system()} {platform.release()}")
        print(f"Python Version: {sys.version}")
        print(f"Current Directory: {os.getcwd()}")
        
        # Check if we're running as admin
        if platform.system() == 'Windows':
            if not is_admin():
                print("\nWarning: Not running as administrator")
                print("Some operations may require admin privileges")
                print("Please run this script as administrator")
        
        # Check if requirements.txt exists
        requirements_path = Path("raspberry_pi/requirements.txt")
        if not requirements_path.exists():
            print(f"\nError: requirements.txt not found at {requirements_path}")
            print("Please make sure you're running the script from the correct directory")
            sys.exit(1)
        
        print("\n=== Power Wheels Control System Setup ===")
        print("This script will help you set up and test the system")
        
        while True:
            print("\nOptions:")
            print("1. Check system requirements")
            print("2. Create virtual environment")
            print("3. Install requirements (virtual environment)")
            print("4. Install requirements (system Python)")
            print("5. Start all processes (using virtual environment)")
            print("6. Start all processes (without virtual environment)")
            print("7. Exit")
            
            try:
                choice = input("\nEnter your choice (1-7): ")
                
                if choice == "1":
                    check_python_version()
                elif choice == "2":
                    create_virtual_environment()
                elif choice == "3":
                    install_requirements(use_venv=True)
                elif choice == "4":
                    install_requirements(use_venv=False)
                elif choice == "5":
                    start_processes(use_venv=True)
                    break  # Exit after starting processes
                elif choice == "6":
                    start_processes(use_venv=False)
                    break  # Exit after starting processes
                elif choice == "7":
                    print("Exiting...")
                    sys.exit(0)
                else:
                    print("Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                continue
            except Exception as e:
                print(f"\nError in menu operation: {str(e)}")
                print("Full error details:")
                import traceback
                traceback.print_exc()
                continue
    
    except Exception as e:
        print("\n=== Fatal Error ===")
        print(f"An unexpected error occurred: {str(e)}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        print("\nPlease check your system configuration and try again")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print("\n=== Fatal Error ===")
        print(f"An unexpected error occurred: {str(e)}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        print("\nPlease check your system configuration and try again")
        input("\nPress Enter to exit...")
        sys.exit(1) 