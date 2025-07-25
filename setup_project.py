#!/usr/bin/env python3

"""
Setup Script

This script creates the necessary directories and files for the project.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import subprocess
from setuptools import setup

def run_command(command):
    """Run a command and return the exit code."""
    print(f"Running command: {command}")
    return subprocess.call(command, shell=True)

def main():
    """Main function to create the necessary directories and files."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the necessary directories
    directories = [
        os.path.join(project_root, 'exports'),
        os.path.join(project_root, 'logs')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Creating directory: {directory}")
            os.makedirs(directory)
        else:
            print(f"Directory already exists: {directory}")
    
    # Create __init__.py files
    print("\nCreating __init__.py files...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if run_command(f"python {os.path.join(script_dir, 'create_init_files.py')}") != 0:
        print("Failed to create __init__.py files. Please check the error messages.")
    
    print("Setup completed successfully.")

if __name__ == "__main__":
    main()
