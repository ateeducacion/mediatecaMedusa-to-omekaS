#!/usr/bin/env python3

"""
Install Requirements Script

This script installs the required packages for the project.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import subprocess
import argparse

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Install Requirements for WordPress to Omeka S Migration')
    parser.add_argument('--upgrade', action='store_true', help='Upgrade packages to the latest version')
    parser.add_argument('--user', action='store_true', help='Install packages in user space')
    return parser.parse_args()

def main():
    """Main function to install the required packages."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Get the requirements file path
    requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
    
    # Build the command
    command = "pip install"
    
    if args.upgrade:
        command += " --upgrade"
    
    if args.user:
        command += " --user"
    
    command += f" -r {requirements_file}"
    
    # Run the command
    print(f"Running command: {command}")
    result = subprocess.call(command, shell=True)
    
    # Return non-zero exit code if command failed
    if result != 0:
        print("Failed to install requirements. Please check the error messages.")
        sys.exit(result)
    
    print("Requirements installed successfully.")

if __name__ == "__main__":
    main()
