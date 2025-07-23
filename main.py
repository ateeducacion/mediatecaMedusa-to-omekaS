#!/usr/bin/env python3

"""
WordPress to Omeka S Migration Tool

This script automates the migration of WordPress sites to Omeka S.
It reads a CSV file with channel information and performs the migration process.

Usage:
    python main.py --csv <csv_file> --omeka-url <omeka_url> --wp-username <username> --wp-password <password>

Author: [Your Name]
Date: 23-07-2025
"""

import argparse
import logging
import sys
from src.csv_reader import CSVReader
from src.migration_manager import MigrationManager
from src.logger import setup_logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='WordPress to Omeka S Migration Tool')
    parser.add_argument('--csv', required=True, help='Path to CSV file with channel information')
    parser.add_argument('--omeka-url', required=True, help='Omeka S API URL')
    parser.add_argument('--wp-username', required=True, help='WordPress username')
    parser.add_argument('--wp-password', required=True, help='WordPress password')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    return parser.parse_args()

def main():
    """Main function to run the migration process."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logger
    logger = setup_logger(args.log_level)
    logger.info("Starting WordPress to Omeka S migration process")
    
    try:
        # Read CSV file
        csv_reader = CSVReader(args.csv)
        channels = csv_reader.read_channels()
        logger.info(f"Found {len(channels)} channels to migrate")
        
        # Create migration manager
        migration_manager = MigrationManager(
            omeka_url=args.omeka_url,
            wp_username=args.wp_username,
            wp_password=args.wp_password,
            logger=logger
        )
        
        # Perform migration for each channel
        for channel in channels:
            logger.info(f"Migrating channel: {channel['name']}")
            migration_manager.migrate_channel(channel)
        
        logger.info("Migration process completed successfully")
        
    except Exception as e:
        logger.error(f"Error during migration process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
