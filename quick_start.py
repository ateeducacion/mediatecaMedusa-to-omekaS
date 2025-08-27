#!/usr/bin/env python3

"""
Quick Start Script

This script provides a quick way to set up the project and run a test migration.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import argparse
import subprocess

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Quick Start WordPress to Omeka S Migration')
    parser.add_argument('--omeka-url', required=True, help='Omeka S API URL')
    parser.add_argument('--key-identity', required=True, help='Omeka S API key identity')
    parser.add_argument('--key-credential', required=True, help='Omeka S API key credential')
    parser.add_argument('--wp-username', required=True, help='WordPress username')
    parser.add_argument('--wp-password', required=True, help='WordPress password')
    parser.add_argument('--channel-url', required=True, help='URL of the channel')
    parser.add_argument('--config', default='migration_config.json', help='Path to migration configuration file (default: migration_config.json)')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    # --as-task parameter removed, behavior is now always as if --as-task=y
    parser.add_argument('--execute-tasks', type=str,
                        help='JSON string with bulk_import_ids to execute: \'{"bulk_import_id":[1,2,3]}\'')
    parser.add_argument('--output-file', type=str,
                        help='Path to the output JSON file with migration results')
    return parser.parse_args()

def run_command(command):
    """Run a command and return the exit code."""
    print(f"Running command: {command}")
    return subprocess.call(command, shell=True)

def main():  
    """Main function to set up the project and run a test migration."""
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
    if run_command("python setup_project.py") != 0:
        print("Setup failed. Please check the error messages and try again.")
        return
    
    # Run test migration
    print("\nRunning test migration...")
    command = f"python run_test_migration.py --omeka-url {args.omeka_url} --key-identity {args.key_identity} --key-credential {args.key_credential} --wp-username {args.wp_username} --wp-password {args.wp_password} --channel-url {args.channel_url} --config {args.config} --log-level {args.log_level}"
    
    # Add execute-tasks parameter if provided
    if args.execute_tasks:
        # Ensure proper JSON escaping for command line
        escaped_tasks = args.execute_tasks.replace('"', '\\"')
        command += f" --execute-tasks \"{escaped_tasks}\""
    
    # Add output-file parameter if provided
    if args.output_file:
        command += f" --output-file {args.output_file}"
    
    if run_command(command) != 0:
        print("Test migration failed. Please check the error messages and try again.")
        return
    
    print("\nQuick start completed successfully.")

if __name__ == "__main__":
    main()
