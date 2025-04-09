"""
Installation and Requirements Script for Mission Impossible Supercut Application.

This script installs all required dependencies for the application.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible."""
    required_version = (3, 9)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"Python version check passed: {current_version[0]}.{current_version[1]}")
    return True

def install_requirements():
    """Install required Python packages."""
    requirements = [
        "moviepy",
        "opencv-python",
        "scenedetect[opencv]",
        "torch",
        "torchvision",
        "pillow",
        "numpy"
    ]
    
    print("Installing required packages...")
    
    for package in requirements:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Error installing {package}")
            return False
    
    print("All packages installed successfully")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        if result.returncode == 0:
            print("FFmpeg is installed")
            return True
        else:
            print("FFmpeg is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("FFmpeg is not installed or not in PATH")
        return False

def install_ffmpeg():
    """Attempt to install FFmpeg."""
    system = platform.system().lower()
    
    if system == "linux":
        print("Installing FFmpeg on Linux...")
        try:
            subprocess.check_call(["sudo", "apt-get", "update"])
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "ffmpeg"])
            print("FFmpeg installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Error installing FFmpeg. Please install it manually.")
            return False
    
    elif system == "darwin":  # macOS
        print("Installing FFmpeg on macOS...")
        try:
            # Check if Homebrew is installed
            result = subprocess.run(["brew", "--version"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                # Install FFmpeg using Homebrew
                subprocess.check_call(["brew", "install", "ffmpeg"])
                print("FFmpeg installed successfully")
                return True
            else:
                print("Homebrew is not installed. Please install FFmpeg manually.")
                return False
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error installing FFmpeg. Please install it manually.")
            return False
    
    elif system == "windows":
        print("On Windows, please install FFmpeg manually:")
        print("1. Download FFmpeg from https://ffmpeg.org/download.html")
        print("2. Extract the files to a folder (e.g., C:\\ffmpeg)")
        print("3. Add the bin folder to your PATH environment variable")
        return False
    
    else:
        print(f"Unsupported operating system: {system}")
        print("Please install FFmpeg manually")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        "output",
        "samples"
    ]
    
    print("Creating directories...")
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")
    
    return True

def main():
    """Main function."""
    print("Mission Impossible Supercut Application - Setup")
    print("=============================================")
    
    # Check Python version
    if not check_python_version():
        print("Setup failed: Python version check failed")
        return False
    
    # Install required packages
    if not install_requirements():
        print("Setup failed: Error installing required packages")
        return False
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("FFmpeg not found. Attempting to install...")
        if not install_ffmpeg():
            print("Warning: FFmpeg installation failed.")
            print("The application may not work correctly without FFmpeg.")
            print("Please install FFmpeg manually and add it to your PATH.")
    
    # Create directories
    if not create_directories():
        print("Setup failed: Error creating directories")
        return False
    
    print("\nSetup completed successfully!")
    print("You can now run the application using:")
    print("  - Command line: python src/main.py")
    print("  - GUI: python src/gui.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
