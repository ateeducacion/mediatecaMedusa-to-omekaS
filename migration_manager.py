#!/usr/bin/env python3

"""
Migration Manager Module

This module manages the migration process from WordPress to Omeka S.

Author: [Your Name]
Date: 23-07-2025
"""

import logging
import os
from typing import Dict, Any, List, Optional
from src.Omeka.OmekaAdapter import OmekaAdapter
from src.WordPress.WordPressExporter import WordPressExporter

class MigrationManager:
    """Class to manage the migration process from WordPress to Omeka S."""
    
    def __init__(self, omeka_url: str, wp_username: str, wp_password: str, 
                 key_identity: Optional[str] = None, key_credential: Optional[str] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the migration manager.
        
        Args:
            omeka_url: The URL of the Omeka S API.
            wp_username: The username for WordPress authentication.
            wp_password: The password for WordPress authentication.
            key_identity: The identity key for Omeka S API authentication (optional).
            key_credential: The credential key for Omeka S API authentication (optional).
            logger: A logger instance (optional).
        """
        self.omeka_adapter = OmekaAdapter(omeka_url, key_identity, key_credential)
        self.wp_exporter = WordPressExporter(wp_username, wp_password)
        self.logger = logger or logging.getLogger(__name__)
        
        # Create exports directory if it doesn't exist
        self.exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exports')
        os.makedirs(self.exports_dir, exist_ok=True)
    
    def migrate_channel(self, channel: Dict[str, str]) -> Dict[str, Any]:
        """
        Migrate a WordPress channel to Omeka S.
        
        Args:
            channel: A dictionary containing channel information.
                - name: Name of the channel
                - url: Web address of the channel
                - slug: Slug of the channel
                - editor: Username of the editor
            
        Returns:
            A dictionary containing the migration results.
        """
        self.logger.info(f"Starting migration for channel: {channel['name']}")
        
        # Step 1: Create site in Omeka S
        site = self._create_site(channel['name'], channel['slug'])
        
        # Step 2: Create editor user in Omeka S
        user = self._create_user(channel['editor'])
        
        # Step 3: Add user to site
        self._add_user_to_site(site['o:id'], user['o:id'])
        
        # Step 4: Export WordPress data
        xml_file = self._export_wordpress_data(channel['url'])
        
        # Step 5: Prepare for future job creation (to be implemented in future iterations)
        self._prepare_for_job_creation(site['o:id'], xml_file)
        
        # Return migration results
        results = {
            'channel': channel,
            'site': site,
            'user': user,
            'xml_file': xml_file
        }
        
        self.logger.info(f"Migration completed for channel: {channel['name']}")
        
        return results
    
    def _create_site(self, name: str, slug: str) -> Dict[str, Any]:
        """
        Create a site in Omeka S.
        
        Args:
            name: The name of the site.
            slug: The slug of the site.
            
        Returns:
            The created site data.
        """
        self.logger.info(f"Creating site in Omeka S: {name}")
        
        # Check if site already exists
        existing_site = self.omeka_adapter.get_site_by_slug(slug)
        if existing_site:
            self.logger.warning(f"Site already exists: {name} (ID: {existing_site['o:id']})")
            return existing_site
        
        # Create site
        site = self.omeka_adapter.create_site(name, slug)
        
        self.logger.info(f"Site created: {name} (ID: {site['o:id']})")
        
        return site
    
    def _create_user(self, username: str) -> Dict[str, Any]:
        """
        Create a user in Omeka S.
        
        Args:
            username: The username of the editor.
            
        Returns:
            The created user data.
        """
        self.logger.info(f"Creating user in Omeka S: {username}")
        
        # Generate email
        email = f"{username}@gobiernodecanarias.org"
        
        # Check if user already exists
        existing_user = self.omeka_adapter.get_user_by_email(email)
        if existing_user:
            self.logger.warning(f"User already exists: {username} (ID: {existing_user['o:id']})")
            return existing_user
        
        # Create user
        user = self.omeka_adapter.create_user(username, email, "editor")
        
        self.logger.info(f"User created: {username} (ID: {user['o:id']})")
        
        return user
    
    def _add_user_to_site(self, site_id: int, user_id: int) -> Dict[str, Any]:
        """
        Add a user to a site in Omeka S.
        
        Args:
            site_id: The ID of the site.
            user_id: The ID of the user.
            
        Returns:
            The updated site data.
        """
        self.logger.info(f"Adding user (ID: {user_id}) to site (ID: {site_id})")
        
        # Add user to site
        site = self.omeka_adapter.add_user_to_site(site_id, user_id, "viewer")
        
        self.logger.info(f"User (ID: {user_id}) added to site (ID: {site_id})")
        
        return site
    
    def _export_wordpress_data(self, channel_url: str) -> str:
        """
        Export data from a WordPress channel.
        
        Args:
            channel_url: The URL of the WordPress channel.
            
        Returns:
            The path to the exported XML file.
        """
        self.logger.info(f"Exporting data from WordPress: {channel_url}")
        
        # Export data
        xml_file = self.wp_exporter.export_channel_data(channel_url, self.exports_dir)
        
        self.logger.info(f"Data exported to: {xml_file}")
        
        return xml_file
    
    def _prepare_for_job_creation(self, site_id: int, xml_file: str) -> None:
        """
        Prepare for future job creation (to be implemented in future iterations).
        
        Args:
            site_id: The ID of the site.
            xml_file: The path to the exported XML file.
        """
        self.logger.info(f"Preparing for future job creation for site (ID: {site_id})")
        
        # This method will be implemented in future iterations
        # For now, just log that it's a placeholder
        self.logger.info("Job creation will be implemented in future iterations")
        
        # Placeholder for future implementation:
        # 1. Create job for migrating item sets
        # 2. Create job for migrating items
        # 3. Create job for migrating media
        # 4. Execute jobs
