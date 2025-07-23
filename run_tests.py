#!/usr/bin/env python3

"""
Run Tests Script

This script runs all the tests for the project.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import unittest
import argparse

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run Tests for WordPress to Omeka S Migration')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    return parser.parse_args()

def main():
    """Main function to run all the tests."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add the project root directory to the Python path
    sys.path.insert(0, project_root)
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    result = test_runner.run(test_suite)
    
    # Return non-zero exit code if tests failed
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == "__main__":
    main()
