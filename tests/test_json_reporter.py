#!/usr/bin/env python3

"""
Test JSON Reporter

This script tests the JSON reporter functionality by generating a report for a sample channel.

Usage:
    python test_json_reporter.py --output-file <output_file> [--xml-file <xml_file>]

Author: [Your Name]
Date: 26-08-2025
"""

import argparse
import json
import logging
import os
import sys
from src.json_reporter import JSONReporter
from src.logger import setup_logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test JSON Reporter')
    parser.add_argument('--output-file', required=True, help='Path to the output JSON file')
    parser.add_argument('--xml-file', default='exports/ceipabona.xml', help='Path to an XML file to test with')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    return parser.parse_args()

def main():
    """Main function to test the JSON reporter."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logger
    logger = setup_logger(args.log_level)
    logger.info("Starting JSON reporter test")
    
    try:
        # Check if XML file exists
        if not os.path.exists(args.xml_file):
            logger.error(f"XML file not found: {args.xml_file}")
            sys.exit(1)
        
        # Create JSON reporter
        reporter = JSONReporter(args.output_file, logger)
        
        # Create sample channel data
        channel_data = {
            'name': 'Test Channel',
            'url': 'https://example.com/test',
            'slug': 'test-channel',
            'editor': 'test_admin'
        }
        
        # Create sample migration result
        migration_result = {
            'site': {
                'o:id': 123,
                'o:title': 'Test Channel'
            },
            'user': {
                'o:id': 456,
                'o:name': 'test_admin',
                'o:email': 'test_admin@example.com'
            },
            'xml_file': args.xml_file,
            'import_jobs': [
                {
                    'o:id': 789,
                    'o-bulk:importer': {
                        'o:id': 101,
                        'o:label': 'Media Importer'
                    }
                },
                {
                    'o:id': 790,
                    'o-bulk:importer': {
                        'o:id': 102,
                        'o:label': 'Item Importer'
                    }
                }
            ]
        }
        
        # Add channel report
        reporter.add_channel_report(channel_data, migration_result)
        
        # Read and display the generated report
        with open(args.output_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        logger.info(f"Generated report with {len(report_data)} entries")
        logger.info(f"Report saved to: {args.output_file}")
        
        # Display the last entry
        if report_data:
            last_entry = report_data[-1]
            logger.info("Last entry in the report:")
            logger.info(f"  Channel: {last_entry.get('name')}")
            logger.info(f"  Site ID: {last_entry.get('site_id')}")
            logger.info(f"  User ID: {last_entry.get('user_id')}")
            logger.info(f"  Tasks created: {len(last_entry.get('tasks_created', []))}")
            logger.info(f"  Number of itemsets: {last_entry.get('number_of_itemsets')}")
            logger.info(f"  Number of items: {last_entry.get('number_of_items')}")
            logger.info(f"  Number of media: {last_entry.get('number_of_media')}")
        
    except Exception as e:
        logger.error(f"Error during JSON reporter test: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
