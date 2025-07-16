#!/usr/bin/env python3
"""
Setup script for Google Maps scraper dependencies
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_chromedriver():
    """Check if ChromeDriver is available"""
    try:
        subprocess.run(["chromedriver", "--version"], capture_output=True, check=True)
        print("✓ ChromeDriver is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ChromeDriver not found")
        return False

def install_chromedriver_instructions():
    """Print ChromeDriver installation instructions"""
    print("\nChromeDriver Installation:")
    print("1. Download from: https://chromedriver.chromium.org/")
    print("2. Or use Homebrew: brew install chromedriver")
    print("3. Make sure it's in your PATH")

def main():
    print("Setting up Google Maps Scraper...")
    
    # Install Python requirements
    print("Installing Python packages...")
    install_requirements()
    
    # Check ChromeDriver
    if not check_chromedriver():
        install_chromedriver_instructions()
        print("\nPlease install ChromeDriver and run this script again.")
        return False
    
    print("\n✓ Setup complete! You can now run the scraper.")
    return True

if __name__ == "__main__":
    main()