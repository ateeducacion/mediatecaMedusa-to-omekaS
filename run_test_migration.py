#!/usr/bin/env python3

"""
Run Test Migration Script

This script provides a simple way to run a test migration for a single channel.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import argparse

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run Test WordPress to Omeka S Migration')
    parser.add_argument('--omeka-url', required=True, help='Omeka S API URL')
    parser.add_argument('--key-identity', required=True, help='Omeka S API key identity')
    parser.add_argument('--key-credential', required=True, help='Omeka S API key credential')
    parser.add_argument('--wp-username', required=True, help='WordPress username')
    parser.add_argument('--wp-password', required=True, help='WordPress password')
    parser.add_argument('--channel-name', default='Test Channel', help='Name of the channel (default: Test Channel)')
    parser.add_argument('--channel-url', required=True, help='URL of the channel')
    parser.add_argument('--channel-slug', help='Slug of the channel (optional, will be generated from name if not provided)')
    parser.add_argument('--channel-editor', default='test_admin', help='Username of the editor (default: test_admin)')
    parser.add_argument('--config', default='migration_config.json', help='Path to migration configuration file (default: migration_config.json)')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    parser.add_argument('--output-file', type=str,
                        help='Path to the output JSON file with migration results')
    return parser.parse_args()

def main():
    """Main function to run the test migration process."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Build the command to run the test script
    command = f"python src/test_migration.py --omeka-url {args.omeka_url} --key-identity {args.key_identity} --key-credential {args.key_credential} --wp-username {args.wp_username} --wp-password {args.wp_password} --channel-name \"{args.channel_name}\" --channel-url {args.channel_url} --config {args.config} --log-level {args.log_level}"
    
    # Add optional arguments if provided
    if args.channel_slug:
        command += f" --channel-slug {args.channel_slug}"
    
    command += f" --channel-editor {args.channel_editor}"
    
    # Add output-file parameter if provided
    if args.output_file:
        command += f" --output-file {args.output_file}"
    
    # Print the command
    print(f"Running command: {command}")
    
    # Run the command
    os.system(command)

if __name__ == "__main__":
    main()
