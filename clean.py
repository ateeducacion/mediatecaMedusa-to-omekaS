#!/usr/bin/env python3

"""
Clean Script

This script cleans up the project by removing generated files.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import shutil
import argparse

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Clean WordPress to Omeka S Migration Project')
    parser.add_argument('--all', action='store_true', help='Remove all generated files (including logs and exports)')
    return parser.parse_args()

def main():
    """Main function to clean up the project."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Directories to clean
    directories = [
        os.path.join(project_root, 'coverage'),
        os.path.join(project_root, 'docs')
    ]
    
    # Add logs and exports directories if --all is specified
    if args.all:
        directories.extend([
            os.path.join(project_root, 'logs'),
            os.path.join(project_root, 'exports')
        ])
    
    # Remove directories
    for directory in directories:
        if os.path.exists(directory):
            print(f"Removing directory: {directory}")
            shutil.rmtree(directory)
    
    # Files to clean
    files = [
        os.path.join(project_root, '.coverage')
    ]
    
    # Remove files
    for file in files:
        if os.path.exists(file):
            print(f"Removing file: {file}")
            os.remove(file)
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk(project_root):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_dir = os.path.join(root, dir_name)
                print(f"Removing directory: {pycache_dir}")
                shutil.rmtree(pycache_dir)
    
    print("Cleanup completed successfully.")

if __name__ == "__main__":
    main()
