#!/usr/bin/env python3

"""
Test Logger Module

This module contains tests for the logger module.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import unittest
import logging
import tempfile
from src.logger import setup_logger, get_test_logger

class TestLogger(unittest.TestCase):
    """Test case for the logger module."""
    
    def test_setup_logger(self):
        """Test setting up a logger."""
        # Set up a logger
        logger = setup_logger('DEBUG')
        
        # Check the logger level
        self.assertEqual(logger.level, logging.DEBUG)
        
        # Check the number of handlers
        self.assertEqual(len(logger.handlers), 2)
        
        # Check the first handler (console handler)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        self.assertEqual(logger.handlers[0].level, logging.DEBUG)
        
        # Check the second handler (file handler)
        self.assertIsInstance(logger.handlers[1], logging.FileHandler)
        self.assertEqual(logger.handlers[1].level, logging.DEBUG)
        
        # Clean up
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                os.remove(handler.baseFilename)
    
    def test_get_test_logger(self):
        """Test getting a test logger."""
        # Get a test logger
        logger = get_test_logger()
        
        # Check the logger level
        self.assertEqual(logger.level, logging.INFO)
        
        # Check the number of handlers
        self.assertEqual(len(logger.handlers), 1)
        
        # Check the handler (console handler)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        self.assertEqual(logger.handlers[0].level, logging.INFO)

if __name__ == '__main__':
    unittest.main()
