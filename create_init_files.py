#!/usr/bin/env python3

"""
Create Init Files Script

This script creates empty __init__.py files in each directory to make them proper Python packages.

Author: [Your Name]
Date: 23-07-2025
"""

import os

def create_init_files(base_dir):
    for dirpath, dirnames, filenames in os.walk(base_dir):
        init_file = os.path.join(dirpath, '__init__.py')
        if not os.path.exists(init_file):
            print(f"Creating {init_file}")
            os.makedirs(dirpath, exist_ok=True)
            with open(init_file, 'w') as f:
                f.write('# Automatically generated\n')

def main():
    # Carpeta src en la misma ubicación que este script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(script_dir, 'src')
    if not os.path.isdir(src_dir):
        print(f"❌ No se encontró el directorio: {src_dir}")
        return

    create_init_files(src_dir)

if __name__ == "__main__":
    main()
