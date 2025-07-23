#!/usr/bin/env python3

"""
Test WordPress Exporter Module

This module contains tests for the WordPress exporter module.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from src.WordPress.WordPressExporter import WordPressExporter

class TestWordPressExporter(unittest.TestCase):
    """Test case for the WordPress exporter module."""
    
    def setUp(self):
        """Set up the test case."""
        self.username = 'test_user'
        self.password = 'test_password'
        self.exporter = WordPressExporter(self.username, self.password)
    
    @patch('src.WordPress.WordPressExporter.cas_login')
    def test_export_channel_data(self, mock_cas_login):
        """Test exporting channel data."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'test content'
        mock_session.get.return_value = mock_response
        mock_cas_login.return_value = mock_session
        
        # Create a temporary directory
        temp_dir = 'temp_test_dir'
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Call the method
            channel_url = 'https://example.com/channel'
            xml_file = self.exporter.export_channel_data(channel_url, temp_dir)
            
            # Check the result
            self.assertEqual(xml_file, os.path.join(temp_dir, 'channel.xml'))
            self.assertTrue(os.path.exists(xml_file))
            
            # Check the file content
            with open(xml_file, 'rb') as f:
                content = f.read()
                self.assertEqual(content, b'test content')
            
            # Check the mocks were called correctly
            mock_cas_login.assert_called_once_with('https://example.com/channel/wp-admin/export.php', self.username, self.password)
            mock_session.get.assert_called_once_with('https://example.com/channel/wp-admin/export.php', params={'download': 'true', 'content': 'all'})
        
        finally:
            # Clean up
            if os.path.exists(os.path.join(temp_dir, 'channel.xml')):
                os.remove(os.path.join(temp_dir, 'channel.xml'))
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
    
    @patch('src.WordPress.WordPressExporter.cas_login')
    def test_export_channel_data_error(self, mock_cas_login):
        """Test exporting channel data with an error."""
        # Set up the mocks
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        mock_response.raise_for_status.side_effect = Exception('Not found')
        mock_session.get.return_value = mock_response
        mock_cas_login.return_value = mock_session
        
        # Create a temporary directory
        temp_dir = 'temp_test_dir'
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Call the method
            channel_url = 'https://example.com/channel'
            with self.assertRaises(Exception):
                self.exporter.export_channel_data(channel_url, temp_dir)
            
            # Check the mocks were called correctly
            mock_cas_login.assert_called_once_with('https://example.com/channel/wp-admin/export.php', self.username, self.password)
            mock_session.get.assert_called_once_with('https://example.com/channel/wp-admin/export.php', params={'download': 'true', 'content': 'all'})
            mock_response.raise_for_status.assert_called_once()
        
        finally:
            # Clean up
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

if __name__ == '__main__':
    unittest.main()
