#!/usr/bin/env python3

"""
Run Migration Script

This script provides a simple way to run the migration process.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import argparse

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run WordPress to Omeka S Migration')
    parser.add_argument('--csv', default='example_channels.csv', help='Path to CSV file with channel information (default: example_channels.csv)')
    parser.add_argument('--omeka-url', required=True, help='Omeka S API URL')
    parser.add_argument('--wp-username', required=True, help='WordPress username')
    parser.add_argument('--wp-password', required=True, help='WordPress password')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level (default: INFO)')
    return parser.parse_args()

def main():
    """Main function to run the migration process."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Build the command to run the main script
    command = f"python main.py --csv {args.csv} --omeka-url {args.omeka_url} --wp-username {args.wp_username} --wp-password {args.wp_password} --log-level {args.log_level}"
    
    # Print the command
    print(f"Running command: {command}")
    
    # Run the command
    os.system(command)

if __name__ == "__main__":
    main()
