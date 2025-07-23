#!/usr/bin/env python3

"""
Test CSV Reader Module

This module contains tests for the CSV reader module.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import unittest
import tempfile
from src.csv_reader import CSVReader

class TestCSVReader(unittest.TestCase):
    """Test case for the CSV reader module."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv')
        self.temp_file.write('name,url,slug,editor\n')
        self.temp_file.write('Channel 1,https://example.com/channel1,channel1,user1\n')
        self.temp_file.write('Channel 2,https://example.com/channel2,channel2,user2\n')
        self.temp_file.write('Channel 3,https://example.com/channel3,,user3\n')
        self.temp_file.close()
    
    def tearDown(self):
        """Tear down the test case."""
        # Remove the temporary CSV file
        os.unlink(self.temp_file.name)
    
    def test_read_channels(self):
        """Test reading channels from a CSV file."""
        # Create a CSV reader
        csv_reader = CSVReader(self.temp_file.name)
        
        # Read channels
        channels = csv_reader.read_channels()
        
        # Check the number of channels
        self.assertEqual(len(channels), 3)
        
        # Check the first channel
        self.assertEqual(channels[0]['name'], 'Channel 1')
        self.assertEqual(channels[0]['url'], 'https://example.com/channel1')
        self.assertEqual(channels[0]['slug'], 'channel1')
        self.assertEqual(channels[0]['editor'], 'user1')
        
        # Check the second channel
        self.assertEqual(channels[1]['name'], 'Channel 2')
        self.assertEqual(channels[1]['url'], 'https://example.com/channel2')
        self.assertEqual(channels[1]['slug'], 'channel2')
        self.assertEqual(channels[1]['editor'], 'user2')
        
        # Check the third channel (with empty slug)
        self.assertEqual(channels[2]['name'], 'Channel 3')
        self.assertEqual(channels[2]['url'], 'https://example.com/channel3')
        self.assertEqual(channels[2]['slug'], 'channel-3')  # Generated from name
        self.assertEqual(channels[2]['editor'], 'user3')
    
    def test_missing_file(self):
        """Test reading channels from a non-existent file."""
        # Create a CSV reader with a non-existent file
        csv_reader = CSVReader('non_existent_file.csv')
        
        # Try to read channels
        with self.assertRaises(FileNotFoundError):
            csv_reader.read_channels()
    
    def test_missing_columns(self):
        """Test reading channels from a CSV file with missing columns."""
        # Create a temporary CSV file with missing columns
        temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv')
        temp_file.write('name,url\n')
        temp_file.write('Channel 1,https://example.com/channel1\n')
        temp_file.close()
        
        # Create a CSV reader
        csv_reader = CSVReader(temp_file.name)
        
        # Try to read channels
        with self.assertRaises(ValueError):
            csv_reader.read_channels()
        
        # Remove the temporary CSV file
        os.unlink(temp_file.name)

if __name__ == '__main__':
    unittest.main()
