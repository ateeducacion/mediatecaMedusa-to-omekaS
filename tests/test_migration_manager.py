#!/usr/bin/env python3

"""
Test Migration Manager Module

This module contains tests for the migration manager module.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from src.migration_manager import MigrationManager

class TestMigrationManager(unittest.TestCase):
    """Test case for the migration manager module."""
    
    def setUp(self):
        """Set up the test case."""
        self.omeka_url = 'http://example.com/api'
        self.wp_username = 'test_user'
        self.wp_password = 'test_password'
        
        # Create patches
        self.omeka_adapter_patch = patch('src.migration_manager.OmekaAdapter')
        self.wp_exporter_patch = patch('src.migration_manager.WordPressExporter')
        
        # Start patches
        self.mock_omeka_adapter_class = self.omeka_adapter_patch.start()
        self.mock_wp_exporter_class = self.wp_exporter_patch.start()
        
        # Create mock instances
        self.mock_omeka_adapter = MagicMock()
        self.mock_wp_exporter = MagicMock()
        
        # Set up mock classes to return mock instances
        self.mock_omeka_adapter_class.return_value = self.mock_omeka_adapter
        self.mock_wp_exporter_class.return_value = self.mock_wp_exporter
        
        # Create migration manager
        self.manager = MigrationManager(
            omeka_url=self.omeka_url,
            wp_username=self.wp_username,
            wp_password=self.wp_password
        )
    
    def tearDown(self):
        """Tear down the test case."""
        # Stop patches
        self.omeka_adapter_patch.stop()
        self.wp_exporter_patch.stop()
    
    def test_init(self):
        """Test initialization."""
        # Check the adapters were created correctly
        self.mock_omeka_adapter_class.assert_called_once_with(self.omeka_url, None, None)
        self.mock_wp_exporter_class.assert_called_once_with(self.wp_username, self.wp_password)
        
        # Check the exports directory was created
        self.assertTrue(os.path.exists(self.manager.exports_dir))
    
    def test_migrate_channel(self):
        """Test migrating a channel."""
        # Set up mocks
        self.mock_omeka_adapter.get_site_by_slug.return_value = None
        self.mock_omeka_adapter.create_site.return_value = {'o:id': 1, 'o:slug': 'test-channel'}
        self.mock_omeka_adapter.get_user_by_email.return_value = None
        self.mock_omeka_adapter.create_user.return_value = {'o:id': 1, 'o:name': 'test_editor'}
        self.mock_omeka_adapter.add_user_to_site.return_value = {'o:id': 1, 'o:slug': 'test-channel'}
        self.mock_wp_exporter.export_channel_data.return_value = '/path/to/export.xml'
        
        # Call the method
        channel = {
            'name': 'Test Channel',
            'url': 'https://example.com/channel',
            'slug': 'test-channel',
            'editor': 'test_editor'
        }
        results = self.manager.migrate_channel(channel)
        
        # Check the results
        self.assertEqual(results['channel'], channel)
        self.assertEqual(results['site'], {'o:id': 1, 'o:slug': 'test-channel'})
        self.assertEqual(results['user'], {'o:id': 1, 'o:name': 'test_editor'})
        self.assertEqual(results['xml_file'], '/path/to/export.xml')
        
        # Check the mocks were called correctly
        self.mock_omeka_adapter.get_site_by_slug.assert_called_once_with('test-channel')
        self.mock_omeka_adapter.create_site.assert_called_once_with('Test Channel', 'test-channel')
        self.mock_omeka_adapter.get_user_by_email.assert_called_once_with('test_editor@gobiernodecanarias.org')
        self.mock_omeka_adapter.create_user.assert_called_once_with('test_editor', 'test_editor@gobiernodecanarias.org', 'editor')
        self.mock_omeka_adapter.add_user_to_site.assert_called_once_with(1, 1, 'viewer')
        self.mock_wp_exporter.export_channel_data.assert_called_once_with('https://example.com/channel', self.manager.exports_dir)
    
    def test_migrate_channel_existing_site(self):
        """Test migrating a channel with an existing site."""
        # Set up mocks
        self.mock_omeka_adapter.get_site_by_slug.return_value = {'o:id': 1, 'o:slug': 'test-channel'}
        self.mock_omeka_adapter.get_user_by_email.return_value = None
        self.mock_omeka_adapter.create_user.return_value = {'o:id': 1, 'o:name': 'test_editor'}
        self.mock_omeka_adapter.add_user_to_site.return_value = {'o:id': 1, 'o:slug': 'test-channel'}
        self.mock_wp_exporter.export_channel_data.return_value = '/path/to/export.xml'
        
        # Call the method
        channel = {
            'name': 'Test Channel',
            'url': 'https://example.com/channel',
            'slug': 'test-channel',
            'editor': 'test_editor'
        }
        results = self.manager.migrate_channel(channel)
        
        # Check the results
        self.assertEqual(results['channel'], channel)
        self.assertEqual(results['site'], {'o:id': 1, 'o:slug': 'test-channel'})
        self.assertEqual(results['user'], {'o:id': 1, 'o:name': 'test_editor'})
        self.assertEqual(results['xml_file'], '/path/to/export.xml')
        
        # Check the mocks were called correctly
        self.mock_omeka_adapter.get_site_by_slug.assert_called_once_with('test-channel')
        self.mock_omeka_adapter.create_site.assert_not_called()
        self.mock_omeka_adapter.get_user_by_email.assert_called_once_with('test_editor@gobiernodecanarias.org')
        self.mock_omeka_adapter.create_user.assert_called_once_with('test_editor', 'test_editor@gobiernodecanarias.org', 'editor')
        self.mock_omeka_adapter.add_user_to_site.assert_called_once_with(1, 1, 'viewer')
        self.mock_wp_exporter.export_channel_data.assert_called_once_with('https://example.com/channel', self.manager.exports_dir)
    
    def test_migrate_channel_existing_user(self):
        """Test migrating a channel with an existing user."""
        # Set up mocks
        self.mock_omeka_adapter.get_site_by_slug.return_value = None
        self.mock_omeka_adapter.create_site.return_value = {'o:id': 1, 'o:slug': 'test-channel'}
        self.mock_omeka_adapter.get_user_by_email.return_value = {'o:id': 1, 'o:name': 'test_editor'}
        self.mock_omeka_adapter.add_user_to_site.return_value = {'o:id': 1, 'o:slug': 'test-channel'}
        self.mock_wp_exporter.export_channel_data.return_value = '/path/to/export.xml'
        
        # Call the method
        channel = {
            'name': 'Test Channel',
            'url': 'https://example.com/channel',
            'slug': 'test-channel',
            'editor': 'test_editor'
        }
        results = self.manager.migrate_channel(channel)
        
        # Check the results
        self.assertEqual(results['channel'], channel)
        self.assertEqual(results['site'], {'o:id': 1, 'o:slug': 'test-channel'})
        self.assertEqual(results['user'], {'o:id': 1, 'o:name': 'test_editor'})
        self.assertEqual(results['xml_file'], '/path/to/export.xml')
        
        # Check the mocks were called correctly
        self.mock_omeka_adapter.get_site_by_slug.assert_called_once_with('test-channel')
        self.mock_omeka_adapter.create_site.assert_called_once_with('Test Channel', 'test-channel')
        self.mock_omeka_adapter.get_user_by_email.assert_called_once_with('test_editor@gobiernodecanarias.org')
        self.mock_omeka_adapter.create_user.assert_not_called()
        self.mock_omeka_adapter.add_user_to_site.assert_called_once_with(1, 1, 'viewer')
        self.mock_wp_exporter.export_channel_data.assert_called_once_with('https://example.com/channel', self.manager.exports_dir)

if __name__ == '__main__':
    unittest.main()
