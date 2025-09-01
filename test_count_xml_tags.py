#!/usr/bin/env python3

"""
Test Count XML Tags

This script tests the count_xml_tags method of the JSONReporter class.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

from src.json_reporter import JSONReporter
import logging

def main():
    """Main function to test the count_xml_tags method."""
    # Setup logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    
    # XML file to test with
    xml_file = sys.argv[1] if len(sys.argv) > 1 else 'exports/ceipchiguergue.xml'
    
    # Check if XML file exists
    if not os.path.exists(xml_file):
        logger.error(f"XML file not found: {xml_file}")
        sys.exit(1)
    
    # Create JSON reporter
    reporter = JSONReporter('test_output.json', logger)
    
    # Count XML tags
    tag_counts = reporter.count_xml_tags(xml_file)
    
    # Print results
    print(f"XML file: {xml_file}")
    print(f"Number of itemsets: {tag_counts['number_of_itemsets']}")
    print(f"Number of items: {tag_counts['number_of_items']}")
    print(f"Number of media: {tag_counts['number_of_media']}")

if __name__ == "__main__":
    main()
