#!/usr/bin/env python3

"""
WordPress Exporter Module

This module provides functionality to export data from WordPress sites.

Author: [Your Name]
Date: 23-07-2025
"""

import logging
import os
from typing import Optional
from common.CAS_login import cas_login

class WordPressExporter:
    """Class to export data from WordPress sites."""
    
    def __init__(self, username: str, password: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the WordPress exporter.
        
        Args:
            username: The username for WordPress authentication.
            password: The password for WordPress authentication.
            logger: A logger instance (optional).
        """
        self.username = username
        self.password = password
        self.logger = logger or logging.getLogger(__name__)
    
    def export_channel_data(self, channel_url: str, output_dir: str) -> tuple:
        """
        Export data from a WordPress channel.
        
        Args:
            channel_url: The URL of the WordPress channel.
            output_dir: The directory to save the exported data.
            
        Returns:
            A tuple containing:
                - The path to the exported XML file
                - A status flag indicating success (True) or failure (False)
        """
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate the export URL
        export_url = f"{channel_url.rstrip('/')}/wp-admin/export.php"
        
        # Generate output file path
        channel_name = channel_url.rstrip('/').split('/')[-1]
        output_file = os.path.join(output_dir, f"{channel_name}.xml")
        
        try:
            # Login to WordPress
            self.logger.info(f"Logging in to WordPress: {channel_url}")
            session = cas_login(export_url, self.username, self.password)
            
            # Export data
            params = {
                'download': 'true',
                'content': 'all'  # options: all, posts, pages, attachment
            }
            
            self.logger.info(f"Exporting data from WordPress: {channel_url}")
            response = session.get(export_url, params=params)
            
            if response.status_code != 200:
                self.logger.error(f"Failed to export data from WordPress: {channel_url}. Status code: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return output_file, False
            
            # Save the exported data
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Data exported successfully to: {output_file}")
            return output_file, True
            
        except Exception as e:
            self.logger.error(f"Error exporting data from WordPress: {channel_url}. Error: {str(e)}")
            # Create an empty file to indicate the channel was processed but failed
            with open(output_file, 'w') as f:
                f.write(f"<!-- Error exporting data: {str(e)} -->")
            return output_file, False
