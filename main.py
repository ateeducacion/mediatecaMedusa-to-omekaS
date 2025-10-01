#!/usr/bin/env python3

"""
WordPress to Omeka S Migration Tool

This script automates the migration of WordPress sites to Omeka S.
It reads a CSV file with channel information and performs the migration process.

Usage:
    python main.py --csv <csv_file> --omeka-url <omeka_url> --wp-username <username>

Author: [Your Name]
Date: 23-07-2025
"""

import argparse
import logging
import sys
import getpass
from src.csv_reader import CSVReader
from src.migration_manager import MigrationManager
from src.logger import setup_logger
from src.json_reporter import JSONReporter

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='WordPress to Omeka S Migration Tool')
    parser.add_argument('--csv', required=True, help='Path to CSV file with channel information')
    parser.add_argument('--omeka-url', required=True, help='Omeka S API URL')
    parser.add_argument('--key-identity', required=True, help='Omeka S API key identity')
    parser.add_argument('--key-credential', required=True, help='Omeka S API key credential')
    parser.add_argument('--wp-username', required=True, help='WordPress username')
    # Removed --wp-password
    parser.add_argument('--config', help='Path to migration configuration file')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'],
                        help='Set the logging level')
    parser.add_argument('--output-file', type=str, help='Path to the output JSON file with migration results')
    parser.add_argument('--from-date', type=str, help='Date from which to migrate items (format: YYYY-MM-DD)')
    return parser.parse_args()

def main():
    """Main function to run the migration process."""
    args = parse_arguments()

    # Setup logger
    logger = setup_logger(args.log_level)
    logger.info("Starting WordPress to Omeka S migration process")

    try:
        # Prompt for password securely
        password = getpass.getpass("Password: ")
        migration_manager = MigrationManager(
            omeka_url=args.omeka_url,
            wp_username=args.wp_username,
            wp_password=password,
            key_identity=args.key_identity,
            key_credential=args.key_credential,
            config_file=args.config,
            logger=logger,
            as_task=True,
            from_date=args.from_date
        )

        # Normal migration process
        # Read CSV file, ignoring lines that start with '#'
        csv_reader = CSVReader(args.csv)
        channels = csv_reader.read_channels(ignore_comments=True)
        logger.info(f"Found {len(channels)} channels to migrate")

        # Initialize JSON reporter if output file is specified
        json_reporter = None
        if args.output_file:
            logger.info(f"Initializing JSON reporter with output file: {args.output_file}")
            json_reporter = JSONReporter(args.output_file, logger)

        # Perform migration for each channel
        for channel in channels:
            logger.info(f"Migrating channel: {channel['name']}")
            result = migration_manager.migrate_channel(channel)
            if 'import_jobs' in result:
                logger.info(f"Created {len(result['import_jobs'])} bulk import jobs for channel: {channel['name']}")
            if json_reporter:
                logger.info(f"Adding report for channel: {channel['name']}")
                json_reporter.add_channel_report(channel, result)

        logger.info("Migration process completed successfully")

    except Exception as e:
        logger.error(f"Error during migration process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
