#!/usr/bin/env python3

"""
Run All Script

This script runs all the scripts in the correct order.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import subprocess
import argparse

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run All Scripts for WordPress to Omeka S Migration')
    parser.add_argument('--omeka-url', required=True, help='Omeka S API URL')
    parser.add_argument('--wp-username', required=True, help='WordPress username')
    parser.add_argument('--wp-password', required=True, help='WordPress password')
    parser.add_argument('--csv', default='example_channels.csv', help='Path to CSV file with channel information (default: example_channels.csv)')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level (default: INFO)')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    parser.add_argument('--skip-coverage', action='store_true', help='Skip running coverage')
    parser.add_argument('--skip-docs', action='store_true', help='Skip generating documentation')
    return parser.parse_args()

def run_command(command):
    """Run a command and return the exit code."""
    print(f"Running command: {command}")
    return subprocess.call(command, shell=True)

def main():
    """Main function to run all the scripts in the correct order."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Check requirements
    print("Checking requirements...")
    if run_command("python check_requirements.py") != 0:
        print("Some required packages are missing. Attempting to install them...")
        if run_command("python install_requirements.py") != 0:
            print("Failed to install required packages. Please install them manually and try again.")
            return
        print("Required packages installed successfully.")
    
    # Run setup script
    print("\nRunning setup script...")
    if run_command("python setup.py") != 0:
        print("Setup failed. Please check the error messages and try again.")
        return
    
    # Run tests
    if not args.skip_tests:
        print("\nRunning tests...")
        if run_command("python run_tests.py") != 0:
            print("Tests failed. Please check the error messages and try again.")
            return
    
    # Run coverage
    if not args.skip_coverage:
        print("\nRunning coverage...")
        if run_command("python run_coverage.py --html") != 0:
            print("Coverage failed. Please check the error messages and try again.")
            return
    
    # Generate documentation
    if not args.skip_docs:
        print("\nGenerating documentation...")
        if run_command("python generate_docs.py") != 0:
            print("Documentation generation failed. Please check the error messages and try again.")
            return
    
    # Run migration
    print("\nRunning migration...")
    command = f"python main.py --csv {args.csv} --omeka-url {args.omeka_url} --wp-username {args.wp_username} --wp-password {args.wp_password} --log-level {args.log_level}"
    if run_command(command) != 0:
        print("Migration failed. Please check the error messages and try again.")
        return
    
    print("\nAll scripts completed successfully.")

if __name__ == "__main__":
    main()
