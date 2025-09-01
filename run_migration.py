#!/usr/bin/env python3

"""
Run Migration Script

This script provides a simple way to run the migration process.

Author: [Your Name]
Date: 23-07-2025
"""


import argparse
import getpass
import os


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run WordPress to Omeka S Migration')
    parser.add_argument('--csv', default='example_channels.csv', help='Path to CSV file with channel information (default: example_channels.csv)')
    parser.add_argument('--omeka-url', required=True, help='Omeka S API URL')
    parser.add_argument('--key-identity', required=True, help='Omeka S API key identity')
    parser.add_argument('--key-credential', required=True, help='Omeka S API key credential')
    parser.add_argument('--wp-username', required=True, help='WordPress username')
    # wp-password is removed in favor of secure prompt
    parser.add_argument('--config', default='migration_config.json', help='Path to migration configuration file (default: migration_config.json)')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'],
                        help='Set the logging level (default: INFO)')
    parser.add_argument('--output-file', type=str,
                        help='Path to the output JSON file with migration results')
    return parser.parse_args()


def main():
    """Main function to run the migration process."""
    # Parse command line arguments
    args = parse_arguments()

    # Build the command to run the main script
    # wp-password is now prompted in the target script; do not pass via CLI
    command = f"python main.py --csv {args.csv} --omeka-url {args.omeka_url} --key-identity {args.key_identity} --key-credential {args.key_credential} --wp-username {args.wp_username} --config {args.config} --log-level {args.log_level}"
    
    # Add output-file parameter if provided
    if args.output_file:
        command += f" --output-file {args.output_file}"
    
    # Print the command
    print(f"Running command: {command}")
    
    # Run the command
    os.system(command)

if __name__ == "__main__":
    main()
