#!/usr/bin/env python3

"""
Migration Manager Module

This module manages the migration process from WordPress to Omeka S.

Author: [Your Name]
Date: 23-07-2025
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from Omeka.OmekaAdapter import OmekaAdapter
from WordPress.WordPressExporter import WordPressExporter

class MigrationManager:
    """Class to manage the migration process from WordPress to Omeka S."""
    
    def __init__(self, omeka_url: str, wp_username: str, wp_password: str, 
                 key_identity: Optional[str] = None, key_credential: Optional[str] = None,
                 config_file: Optional[str] = None,
                 logger: Optional[logging.Logger] = None,
                 as_task: bool = True,
                 from_date: Optional[str] = None):  # Changed default to True
        """
        Initialize the migration manager.
        
        Args:
            omeka_url: The URL of the Omeka S API.
            wp_username: The username for WordPress authentication.
            wp_password: The password for WordPress authentication.
            key_identity: The identity key for Omeka S API authentication (optional).
            key_credential: The credential key for Omeka S API authentication (optional).
            config_file: Path to the configuration file (optional).
            logger: A logger instance (optional).
            as_task: Whether to save bulk imports as tasks (True) or execute immediately (False).
            from_date: Optional date filter in YYYY-MM-DD format for filtering items to migrate.
        """
        self.omeka_adapter = OmekaAdapter(omeka_url, key_identity, key_credential, logger)
        self.wp_exporter = WordPressExporter(wp_username, wp_password, logger)
        self.logger = logger or logging.getLogger(__name__)
        self.config = None
        self.importers = []
        self.as_task = as_task
        self.from_date = from_date
        
        # Create exports directory if it doesn't exist
        self.exports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exports')
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # Load configuration if provided
        if config_file:
            self.load_config(config_file)
            # Update configuration based on as_task parameter
            self._update_config_for_task_mode()
            # Create importers once during initialization
            self.importers = self.create_bulk_importers()
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to the configuration file.
            
        Returns:
            The loaded configuration.
        """
        self.logger.info(f"Loading configuration from: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
                
            self.logger.info(f"Configuration loaded successfully")
            return self.config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
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
        xml_file, export_success = self._export_wordpress_data(channel['url'])
        
        # Step 5: Create bulk import jobs for this channel
        import_jobs = []
        if self.importers and export_success:
            import_jobs = self._create_bulk_import_jobs_for_channel(
                channel_name=channel['name'],
                site_id=site['o:id'],
                user_id=user['o:id'],
                xml_file=xml_file
            )
        elif not export_success:
            self.logger.warning(f"Skipping import job creation for channel: {channel['name']} due to export failure")
        
        # Return migration results
        results = {
            'channel': channel,
            'site': site,
            'user': user,
            'xml_file': xml_file,
            'import_jobs': import_jobs,
            'importers': self.importers,  # Include importers for reference
            'status': 'success' if export_success else 'error',
            'error_message': 'Failed to export data from WordPress' if not export_success else None
        }
        
        self.logger.info(f"Migration completed for channel: {channel['name']} with status: {results['status']}")
        
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
        user = self.omeka_adapter.create_user(username, email, "site_editor")
        
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
    
    def _export_wordpress_data(self, channel_url: str) -> tuple:
        """
        Export data from a WordPress channel.
        
        Args:
            channel_url: The URL of the WordPress channel.
            
        Returns:
            A tuple containing:
                - The path to the exported XML file
                - A status flag indicating success (True) or failure (False)
        """
        self.logger.info(f"Exporting data from WordPress: {channel_url}")
        
        # Truncate date from YYYY-MM-DD to YYYY-MM for WordPress export (doesn't support day)
        wp_from_date = None
        if self.from_date:
            wp_from_date = self.from_date[:7]  # Get only YYYY-MM
            self.logger.info(f"Truncating date for WordPress export: {self.from_date} -> {wp_from_date}")
        
        # Export data
        xml_file, success = self.wp_exporter.export_channel_data(channel_url, self.exports_dir, wp_from_date)
        
        if success:
            self.logger.info(f"Data exported successfully to: {xml_file}")
        else:
            self.logger.warning(f"Failed to export data from WordPress: {channel_url}. Continuing with migration process.")
        
        return xml_file, success
    
    def _create_bulk_import_jobs_for_channel(self, channel_name: str, site_id: int, user_id: int, xml_file: str) -> List[Dict[str, Any]]:
        """
        Create bulk import jobs for a specific channel.
        
        Args:
            channel_name: The name of the channel.
            site_id: The ID of the site.
            user_id: The ID of the user.
            xml_file: The path to the exported XML file.
            
        Returns:
            A list of created bulk import jobs.
        """
        self.logger.info(f"Creating2 bulk import jobs for channel: {channel_name}")
        
        if not self.importers:
            self.logger.warning("No importers available. Skipping job creation.")
            return []
        
        import_jobs = []
        
        # Convert from_date to min_post_date format if provided (YYYY-MM-DD -> YYYY-MM-DD 00:00:00)
        min_post_date = None
        if self.from_date:
            min_post_date = f"{self.from_date} 00:00:00"
            self.logger.info(f"Using min_post_date filter: {min_post_date}")
        
        for importer in self.importers:
            # Create import job for this channel and importer, passing the site_id
            # to update the SiteId parameter in the import job's xsl_params
            import_job = self.omeka_adapter.create_bulk_import(
                importer_id=importer['o:id'],
                xml_file=xml_file,
                site_name=channel_name,
                owner_id=user_id,
                site_id=site_id,  # Pass the site_id to update the SiteId parameter
                min_post_date=min_post_date  # Pass the min_post_date filter
            )
            import_jobs.append(import_job)
            
            self.logger.info(f"Import job created for channel: {channel_name}, importer: {importer['o:label']} (ID: {import_job['o:id']})")
        
        self.logger.info(f"Created {len(import_jobs)} import jobs for channel: {channel_name}")
        return import_jobs
    
    def create_bulk_importers(self) -> List[Dict[str, Any]]:
        """
        Create bulk importers based on the configuration.
        
        Returns:
            A list of created bulk importers.
        """
        self.logger.info("Creating bulk importers")
        
        if not self.config or 'importers' not in self.config:
            self.logger.warning("No importers configuration found")
            return []
        
        importers = []
        
        for importer_config in self.config['importers']:
            # Check if importer already exists
            label = importer_config.get('o:label')
            existing_importer = self.omeka_adapter.get_bulk_importer_by_label(label)
            
            if existing_importer:
                self.logger.warning(f"Importer already exists: {label} (ID: {existing_importer['o:id']})")
                importers.append(existing_importer)
                continue
            
            # Process mapper if it's specified as a label
            if 'o-bulk:mapper' in importer_config and isinstance(importer_config['o-bulk:mapper'], str) and importer_config['o-bulk:mapper'].startswith('mapping:'):
                # Extract the mapper label from the string (format: "mapping:label")
                mapper_label = importer_config['o-bulk:mapper'].split(':', 1)[1]
                
                # Look up the mapper by label
                mapper = self.omeka_adapter.get_bulk_mapping_by_label(mapper_label)
                
                if mapper:
                    # Replace the mapper string with the mapper object
                    importer_config['o-bulk:mapper'] = {
                        "@type": "o-bulk:Mapping",
                        "o:id": mapper['o:id'],
                        "o:label": mapper['o:label']
                    }
                else:
                    self.logger.warning(f"Mapper with label '{mapper_label}' not found. Using original mapper reference.")
            
            # Create importer
            importer = self.omeka_adapter.create_bulk_importer(importer_config)
            importers.append(importer)
            
            self.logger.info(f"Importer created: {label} (ID: {importer['o:id']})")
        
        return importers
    
    def _update_config_for_task_mode(self):
        """
        Update the configuration based on the as_task parameter.
        """
        if not self.config or 'importers' not in self.config:
            return
        
        task_value = "1" if self.as_task else "0"
        self.logger.info(f"Setting as_task parameter to '{task_value}' for all importers")
        
        for importer_config in self.config['importers']:
            if 'o:config' in importer_config and 'importer' in importer_config['o:config']:
                importer_config['o:config']['importer']['as_task'] = task_value
            else:
                # Create the structure if it doesn't exist
                if 'o:config' not in importer_config:
                    importer_config['o:config'] = {}
                if 'importer' not in importer_config['o:config']:
                    importer_config['o:config']['importer'] = {}
                importer_config['o:config']['importer']['as_task'] = task_value
