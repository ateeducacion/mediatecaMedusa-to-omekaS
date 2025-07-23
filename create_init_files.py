#!/usr/bin/env python3

"""
Create Init Files Script

This script creates empty __init__.py files in each directory to make them proper Python packages.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys

def main():
    """Main function to create empty __init__.py files."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(project_root, 'src')
    
    # Create __init__.py in src directory
    init_file = os.path.join(src_dir, '__init__.py')
    if not os.path.exists(init_file):
        print(f"Creating file: {init_file}")
        with open(init_file, 'w') as f:
            f.write('# This file is intentionally left empty to make the directory a Python package.\n')
    else:
        print(f"File already exists: {init_file}")
    
    # Create __init__.py in each subdirectory
    for root, dirs, files in os.walk(src_dir):
        for dir_name in dirs:
            # Skip directories that start with . or _
            if dir_name.startswith('.') or dir_name.startswith('_'):
                continue
            
            dir_path = os.path.join(root, dir_name)
            init_file = os.path.join(dir_path, '__init__.py')
            
            if not os.path.exists(init_file):
                print(f"Creating file: {init_file}")
                with open(init_file, 'w') as f:
                    f.write('# This file is intentionally left empty to make the directory a Python package.\n')
            else:
                print(f"File already exists: {init_file}")
    
    print("Init files created successfully.")

if __name__ == "__main__":
    main()
