#!/usr/bin/env python3

"""
CSV Reader Module

This module provides functionality to read channel information from a CSV file.

Author: [Your Name]
Date: 23-07-2025
"""

import csv
import logging
from typing import List, Dict, Any

class CSVReader:
    """Class to read channel information from a CSV file."""
    
    def __init__(self, csv_file_path: str):
        """
        Initialize the CSV reader.
        
        Args:
            csv_file_path: Path to the CSV file with channel information.
        """
        self.csv_file_path = csv_file_path
        self.logger = logging.getLogger(__name__)
    
    def read_channels(self) -> List[Dict[str, Any]]:
        """
        Read channel information from the CSV file.
        
        Returns:
            A list of dictionaries containing channel information.
            Each dictionary has the following keys:
            - name: Name of the channel
            - url: Web address of the channel
            - slug: Slug of the channel
            - editor: Username of the editor
        """
        channels = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                
                # Check if required columns exist
                required_columns = ['name', 'url', 'slug', 'editor']
                if not all(column in csv_reader.fieldnames for column in required_columns):
                    missing_columns = [col for col in required_columns if col not in csv_reader.fieldnames]
                    self.logger.error(f"CSV file is missing required columns: {', '.join(missing_columns)}")
                    raise ValueError(f"CSV file is missing required columns: {', '.join(missing_columns)}")
                
                # Read each row
                for row in csv_reader:
                    channel = {
                        'name': row['name'].strip(),
                        'url': row['url'].strip(),
                        'slug': row['slug'].strip() if row['slug'].strip() else self._generate_slug(row['name']),
                        'editor': row['editor'].strip()
                    }
                    
                    # Validate channel data
                    if not channel['name']:
                        self.logger.warning(f"Skipping row with empty channel name: {row}")
                        continue
                    
                    if not channel['url']:
                        self.logger.warning(f"Skipping row with empty URL: {row}")
                        continue
                    
                    channels.append(channel)
                    self.logger.debug(f"Read channel: {channel['name']}")
            
            return channels
            
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {self.csv_file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {str(e)}")
            raise
    
    def _generate_slug(self, name: str) -> str:
        """
        Generate a slug from the channel name.
        
        Args:
            name: Name of the channel.
            
        Returns:
            A slug generated from the name.
        """
        # Replace spaces with hyphens and convert to lowercase
        slug = name.lower().replace(' ', '-')
        # Remove any characters that are not alphanumeric or hyphens
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        return slug
