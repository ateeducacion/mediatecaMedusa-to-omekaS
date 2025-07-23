#!/usr/bin/env python3

"""
Logger Module

This module provides logging functionality for the migration process.

Author: [Your Name]
Date: 23-07-2025
"""

import logging
import os
import sys
from datetime import datetime

def setup_logger(log_level: str = 'INFO') -> logging.Logger:
    """
    Set up and configure the logger.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        
    Returns:
        A configured logger instance.
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger('migration')
    logger.setLevel(getattr(logging, log_level))
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(logs_dir, f'migration_{timestamp}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level))
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging to {log_file}")
    
    return logger

def get_test_logger() -> logging.Logger:
    """
    Get a logger for testing purposes.
    
    Returns:
        A configured logger instance for testing.
    """
    # Configure test logger
    test_logger = logging.getLogger('migration_test')
    test_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    test_logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - TEST - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    test_logger.addHandler(console_handler)
    
    return test_logger
