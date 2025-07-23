#!/usr/bin/env python3

"""
Run Coverage Script

This script runs all the tests and generates a coverage report.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import subprocess
import argparse

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run Tests with Coverage for WordPress to Omeka S Migration')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    return parser.parse_args()

def main():
    """Main function to run all the tests and generate a coverage report."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add the project root directory to the Python path
    sys.path.insert(0, project_root)
    
    # Check if coverage is installed
    try:
        import coverage
    except ImportError:
        print("Coverage is not installed. Please install it with:")
        print("  pip install coverage")
        sys.exit(1)
    
    # Create coverage directory if it doesn't exist
    coverage_dir = os.path.join(project_root, 'coverage')
    os.makedirs(coverage_dir, exist_ok=True)
    
    # Run coverage
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if args.html:
        command = f"coverage run --source=src --omit=src/tests/* {os.path.join(script_dir, 'run_tests.py')} && coverage html -d coverage"
    else:
        command = f"coverage run --source=src --omit=src/tests/* {os.path.join(script_dir, 'run_tests.py')} && coverage report"
    
    # Run the command
    print(f"Running command: {command}")
    result = subprocess.call(command, shell=True)
    
    # Return non-zero exit code if tests failed
    if result != 0:
        sys.exit(result)
    
    # Print coverage report location
    if args.html:
        print(f"\nCoverage report generated at: {os.path.join(coverage_dir, 'index.html')}")

if __name__ == "__main__":
    main()
