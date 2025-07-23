#!/usr/bin/env python3

"""
Generate Documentation Script

This script generates documentation for the project using pdoc.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import subprocess
import argparse

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate Documentation for WordPress to Omeka S Migration')
    parser.add_argument('--output-dir', default='docs', help='Output directory for documentation (default: docs)')
    return parser.parse_args()

def main():
    """Main function to generate documentation for the project."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add the project root directory to the Python path
    sys.path.insert(0, project_root)
    
    # Check if pdoc is installed
    try:
        import pdoc
    except ImportError:
        print("pdoc is not installed. Please install it with:")
        print("  pip install pdoc")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_root, args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate documentation
    command = f"pdoc --output-dir {output_dir} src"
    
    # Run the command
    print(f"Running command: {command}")
    result = subprocess.call(command, shell=True)
    
    # Return non-zero exit code if command failed
    if result != 0:
        sys.exit(result)
    
    # Print documentation location
    print(f"\nDocumentation generated at: {os.path.join(output_dir, 'src', 'index.html')}")

if __name__ == "__main__":
    main()
