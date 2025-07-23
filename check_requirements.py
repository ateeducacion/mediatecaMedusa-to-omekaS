#!/usr/bin/env python3

"""
Check Requirements Script

This script checks if the required packages are installed.

Author: [Your Name]
Date: 23-07-2025
"""

import importlib
import sys
import os

def check_package(package_name):
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def main():
    """Main function to check if the required packages are installed."""
    # Get the requirements file path
    requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
    
    # Read the requirements file
    with open(requirements_file, 'r') as f:
        requirements = f.readlines()
    
    # Check each package
    missing_packages = []
    for requirement in requirements:
        requirement = requirement.strip()
        if not requirement or requirement.startswith('#'):
            continue
        
        # Extract package name (remove version specifier)
        package_name = requirement.split('>=')[0].split('==')[0].strip()
        
        if not check_package(package_name):
            missing_packages.append(requirement)
    
    # Print results
    if missing_packages:
        print("The following packages are missing:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nYou can install them with:")
        print(f"  pip install -r {requirements_file}")
        return False
    else:
        print("All required packages are installed.")
        return True

if __name__ == "__main__":
    if not main():
        sys.exit(1)
