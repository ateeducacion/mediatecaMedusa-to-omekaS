#!/usr/bin/env python3

"""
Channel Download Script

This script downloads export files for channels listed in exports/mediatecas.csv
using the WordPressExporter module.

Usage:
    python download_channels.py --username USERNAME --password PASSWORD [--start CHANNEL_NUMBER]

Example:
    python download_channels.py --username user@example.com --password mypassword --start 10
"""

import argparse
import csv
import logging
import os
import sys
import time
import getpass
from typing import List, Dict, Optional

from src.WordPress.WordPressExporter import WordPressExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('download_channels.log')
    ]
)
logger = logging.getLogger('download_channels')

def read_channels_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    Read the channels CSV file and return a list of channel dictionaries.
    
    Args:
        csv_path: Path to the CSV file containing channel information.
        
    Returns:
        A list of dictionaries, each containing channel information.
    """
    channels = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                channels.append(row)
        logger.info(f"Successfully read {len(channels)} channels from {csv_path}")
        return channels
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_path}: {e}")
        raise

def download_channel_exports(
    channels: List[Dict[str, str]], 
    username: str, 
    password: str, 
    output_dir: str, 
    start_channel: Optional[int] = None,
    stop_channel: Optional[int] = None
) -> None:
    """
    Download exports for all channels using the WordPress exporter.
    
    Args:
        channels: List of channel dictionaries.
        username: Username for WordPress authentication.
        password: Password for WordPress authentication.
        output_dir: Directory to save the exported files.
        start_channel: Optional channel number to start from.
    """
    # Create the WordPress exporter
    logger.info(f"initializing exporter for user {username}")
    exporter = WordPressExporter(username, password, logger)
    logger.info(f"Exporter initialized for user {username}")
    
    # Get column names from the first channel
    column_keys = list(channels[0].keys())
    num_key = column_keys[0]  # First column is the number
    name_key = column_keys[1]  # Second column is the name
    url_key = column_keys[2]   # Third column is the URL
    
    # Filter channels based on start_channel and stop_channel
    if start_channel is not None or stop_channel is not None:
        filtered_channels = []
        for ch in channels:
            channel_num = int(ch[num_key])
            if start_channel is not None and channel_num < start_channel:
                continue
            if stop_channel is not None and channel_num > stop_channel:
                continue
            filtered_channels.append(ch)
        
        channels = filtered_channels
        
        if start_channel is not None and stop_channel is not None:
            logger.info(f"Processing channels from {start_channel} to {stop_channel}, {len(channels)} channels to process")
        elif start_channel is not None:
            logger.info(f"Starting from channel number {start_channel}, {len(channels)} channels to process")
        elif stop_channel is not None:
            logger.info(f"Processing channels up to {stop_channel}, {len(channels)} channels to process")
    
    total_channels = len(channels)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Download exports for each channel
    for i, channel in enumerate(channels, 1):
        channel_num = channel[num_key]
        channel_name = channel[name_key]
        channel_url = channel[url_key]
        
        logger.info(f"Processing channel {i}/{total_channels}: {channel_name} (#{channel_num})")
        
        try:
            # Show progress information
            print(f"\n[{i}/{total_channels}] Downloading channel: {channel_name} (#{channel_num})")
            print(f"URL: {channel_url}")
            
            start_time = time.time()
            
            # Export the channel data
            output_file = exporter.export_channel_data(channel_url, output_dir)
            
            elapsed_time = time.time() - start_time
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
            
            print(f"✓ Download complete: {output_file}")
            print(f"  File size: {file_size:.2f} MB")
            print(f"  Time taken: {elapsed_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error exporting channel {channel_name} (#{channel_num}): {e}")
            print(f"✗ Error downloading channel {channel_name} (#{channel_num}): {e}")

def main():
    """Main function to parse arguments and run the download process."""
    parser = argparse.ArgumentParser(description='Download WordPress channel exports.')
    parser.add_argument('--username', required=True, help='Username for WordPress authentication')
    parser.add_argument('--start', type=int, help='Channel number to start from')
    parser.add_argument('--stop', type=int, help='Channel number to stop at')
    parser.add_argument('--output-dir', default='exports/channels', help='Directory to save exported files')
    parser.add_argument('--csv-path', default='exports/mediatecas.csv', help='Path to the CSV file with channel information')
    
    args = parser.parse_args()
    try:
        # Read the channels from the CSV file
        channels = read_channels_csv(args.csv_path)
        
        # Prompt for password securely (no echo)
        password = getpass.getpass("Password: ")
        
        # Download the channel exports
        download_channel_exports(
            channels, 
            args.username, 
            password, 
            args.output_dir, 
            args.start,
            args.stop
        )
        
        logger.info("Channel download process completed successfully")
        print("\nChannel download process completed successfully!")
        
    except Exception as e:
        logger.error(f"An error occurred during the download process: {e}")
        print(f"\nAn error occurred during the download process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
