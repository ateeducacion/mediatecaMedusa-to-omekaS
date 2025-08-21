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
    parser.add_argument('--key-identity', required=True, help='Omeka S API key identity')
    parser.add_argument('--key-credential', required=True, help='Omeka S API key credential')
    parser.add_argument('--wp-username', required=True, help='WordPress username')
    parser.add_argument('--wp-password', required=True, help='WordPress password')
    parser.add_argument('--config', help='Path to migration configuration file')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    parser.add_argument('--as-task', choices=['y', 'n'], default='n', 
                        help='Save as task (y) or execute immediately (n). Default: n')
    parser.add_argument('--execute-tasks', type=str,
                        help='JSON string with bulk_import_ids to execute: \'{"bulk_import_id":[1,2,3]}\'')
    return parser.parse_args()

def main():
    """Main function to run the migration process."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logger
    logger = setup_logger(args.log_level)
    logger.info("Starting WordPress to Omeka S migration process")
    
    try:
        # Create migration manager
        migration_manager = MigrationManager(
            omeka_url=args.omeka_url,
            wp_username=args.wp_username,
            wp_password=args.wp_password,
            key_identity=args.key_identity,
            key_credential=args.key_credential,
            config_file=args.config,
            logger=logger,
            as_task=(args.as_task == 'y')
        )
        
        # Handle execute-tasks mode
        if args.execute_tasks:
            import json
            try:
                tasks_data = json.loads(args.execute_tasks)
                bulk_import_ids = tasks_data.get('bulk_import_id', [])
                logger.info(f"Executing {len(bulk_import_ids)} bulk import tasks")
                
                results = migration_manager.execute_bulk_import_tasks(bulk_import_ids)
                for result in results:
                    if result['success']:
                        logger.info(f"Task {result['bulk_import_id']} executed successfully")
                    else:
                        logger.error(f"Task {result['bulk_import_id']} failed: {result['error']}")
                
                logger.info("Task execution completed")
                return
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON format for --execute-tasks: {str(e)}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Error executing tasks: {str(e)}")
                sys.exit(1)
        
        # Normal migration process
        # Read CSV file
        csv_reader = CSVReader(args.csv)
        channels = csv_reader.read_channels()
        logger.info(f"Found {len(channels)} channels to migrate")
        
        # Perform migration for each channel
        for channel in channels:
            logger.info(f"Migrating channel: {channel['name']}")
            result = migration_manager.migrate_channel(channel)
            if 'import_jobs' in result:
                logger.info(f"Created {len(result['import_jobs'])} bulk import jobs for channel: {channel['name']}")
        
        logger.info("Migration process completed successfully")
        
    except Exception as e:
        logger.error(f"Error during migration process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
