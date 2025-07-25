#!/usr/bin/env python3

"""
Test Migration Module

This module provides functionality to test the migration process.

Author: [Your Name]
Date: 23-07-2025
"""

import argparse
import logging
import sys
import json
from logger import get_test_logger
from migration_manager import MigrationManager

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test WordPress to Omeka S Migration')
    parser.add_argument('--omeka-url', required=True, help='Omeka S API URL')
    parser.add_argument('--key-identity', required=True, help='Omeka S API key identity')
    parser.add_argument('--key-credential', required=True, help='Omeka S API key credential')
    parser.add_argument('--wp-username', required=True, help='WordPress username')
    parser.add_argument('--wp-password', required=True, help='WordPress password')
    parser.add_argument('--channel-name', required=True, help='Name of the channel')
    parser.add_argument('--channel-url', required=True, help='URL of the channel')
    parser.add_argument('--channel-slug', help='Slug of the channel (optional, will be generated from name if not provided)')
    parser.add_argument('--channel-editor', required=True, help='Username of the editor')
    parser.add_argument('--config', help='Path to migration configuration file')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    return parser.parse_args()

def main():
    """Main function to test the migration process."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logger
    logger = get_test_logger(args.log_level)
    logger.info("Starting test migration process")
    
    try:
        # Create migration manager
        migration_manager = MigrationManager(
            omeka_url=args.omeka_url,
            wp_username=args.wp_username,
            wp_password=args.wp_password,
            key_identity=args.key_identity,
            key_credential=args.key_credential,
            config_file=args.config,
            logger=logger
        )
        
        # Create channel data
        channel = {
            'name': args.channel_name,
            'url': args.channel_url,
            'slug': args.channel_slug or args.channel_name.lower().replace(' ', '-'),
            'editor': args.channel_editor
        }
        
        # Perform migration
        logger.info(f"Migrating channel: {channel['name']}")
        results = migration_manager.migrate_channel(channel)
        
        # Print results
        logger.info("Migration results:")
        logger.info(f"Channel: {results['channel']['name']}")
        logger.info(f"Site ID: {results['site']['o:id']}")
        logger.info(f"User ID: {results['user']['o:id']}")
        logger.info(f"XML file: {results['xml_file']}")
        
        # Test site creation
        logger.info("Testing site creation...")
        site = migration_manager.omeka_adapter.get_site_by_slug(channel['slug'])
        if site:
            logger.info(f"Site test passed: Site exists with ID {site['o:id']}")
        else:
            logger.error("Site test failed: Site does not exist")
        
        # Test user creation
        logger.info("Testing user creation...")
        user = migration_manager.omeka_adapter.get_user_by_email(f"{channel['editor']}@gobiernodecanarias.org")
        if user:
            logger.info(f"User test passed: User exists with ID {user['o:id']}")
        else:
            logger.error("User test failed: User does not exist")
        
        logger.info("Test migration process completed successfully")
        
    except Exception as e:
        logger.error(f"Error during test migration process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
