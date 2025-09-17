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
    
    def read_channels(self, ignore_comments: bool = False) -> List[Dict[str, Any]]:
        """
        Read channel information from the CSV file.
        
        Args:
            ignore_comments: Whether to ignore lines starting with '#' (default: False).
            
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
                # If ignore_comments is True, filter out lines starting with '#'
                if ignore_comments:
                    # Read all lines and filter out comment lines
                    lines = [line for line in csv_file if not line.strip().startswith('#')]
                    # Create a new csv reader from the filtered lines
                    csv_reader = csv.DictReader(lines)
                else:
                    csv_reader = csv.DictReader(csv_file)
                
                # Check if required columns exist
                required_columns = ['name', 'url', 'slug', 'editor']
                if not csv_reader.fieldnames or not all(column in csv_reader.fieldnames for column in required_columns):
                    missing_columns = [col for col in required_columns if not csv_reader.fieldnames or col not in csv_reader.fieldnames]
                    self.logger.error(f"CSV file is missing required columns: {', '.join(missing_columns)}")
                    raise ValueError(f"CSV file is missing required columns: {', '.join(missing_columns)}")
                
                # Read each row
                for row in csv_reader:
                    # Skip rows with missing required fields
                    if 'name' not in row or 'url' not in row or 'editor' not in row:
                        self.logger.warning(f"Skipping row with missing required fields: {row}")
                        continue
                    
                    # Handle None values
                    name = row['name'].strip() if row['name'] else ''
                    url = row['url'].strip() if row['url'] else ''
                    slug = row['slug'].strip() if row.get('slug') else ''
                    editor = row['editor'].strip() if row['editor'] else ''
                    
                    channel = {
                        'name': name,
                        'url': url,
                        'slug': slug if slug else self._generate_slug(name),
                        'editor': editor
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
