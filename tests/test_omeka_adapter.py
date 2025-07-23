#!/usr/bin/env python3

"""
Test Omeka Adapter Module

This module contains tests for the Omeka adapter module.

Author: [Your Name]
Date: 23-07-2025
"""

import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock
from src.Omeka.OmekaAdapter import OmekaAdapter

class TestOmekaAdapter(unittest.TestCase):
    """Test case for the Omeka adapter module."""
    
    def setUp(self):
        """Set up the test case."""
        self.api_url = 'http://example.com/api'
        self.adapter = OmekaAdapter(self.api_url)
    
    @patch('src.Omeka.OmekaAdapter.requests.request')
    def test_create_site(self, mock_request):
        """Test creating a site."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'o:id': 1,
            'o:slug': 'test-site',
            'o:title': 'Test Site'
        }
        mock_request.return_value = mock_response
        
        # Call the method
        site = self.adapter.create_site('Test Site', 'test-site')
        
        # Check the result
        self.assertEqual(site['o:id'], 1)
        self.assertEqual(site['o:slug'], 'test-site')
        self.assertEqual(site['o:title'], 'Test Site')
        
        # Check the mock was called correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'POST')
        self.assertEqual(kwargs['url'], 'http://example.com/api/sites')
        self.assertEqual(kwargs['headers'], {'Content-Type': 'application/json'})
        
        # Check the data
        data = json.loads(kwargs['data'])
        self.assertEqual(data['o:title'], 'Test Site')
        self.assertEqual(data['o:slug'], 'test-site')
        self.assertEqual(data['o:theme'], 'freedom')
        self.assertEqual(data['o:is_public'], True)
        self.assertEqual(data['o:assign_new_items'], False)
        self.assertEqual(data['o:owner'], {'o:id': 1})
    
    @patch('src.Omeka.OmekaAdapter.requests.request')
    def test_create_user(self, mock_request):
        """Test creating a user."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'o:id': 1,
            'o:name': 'Test User',
            'o:email': 'test@example.com',
            'o:role': 'editor'
        }
        mock_request.return_value = mock_response
        
        # Call the method
        user = self.adapter.create_user('Test User', 'test@example.com', 'editor')
        
        # Check the result
        self.assertEqual(user['o:id'], 1)
        self.assertEqual(user['o:name'], 'Test User')
        self.assertEqual(user['o:email'], 'test@example.com')
        self.assertEqual(user['o:role'], 'editor')
        
        # Check the mock was called correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'POST')
        self.assertEqual(kwargs['url'], 'http://example.com/api/users')
        self.assertEqual(kwargs['headers'], {'Content-Type': 'application/json'})
        
        # Check the data
        data = json.loads(kwargs['data'])
        self.assertEqual(data['o:name'], 'Test User')
        self.assertEqual(data['o:email'], 'test@example.com')
        self.assertEqual(data['o:role'], 'editor')
        self.assertEqual(data['o:is_active'], True)
    
    @patch('src.Omeka.OmekaAdapter.requests.request')
    def test_get_site_by_slug(self, mock_request):
        """Test getting a site by slug."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'o:id': 1,
                'o:slug': 'site1',
                'o:title': 'Site 1'
            },
            {
                'o:id': 2,
                'o:slug': 'site2',
                'o:title': 'Site 2'
            }
        ]
        mock_request.return_value = mock_response
        
        # Call the method
        site = self.adapter.get_site_by_slug('site2')
        
        # Check the result
        self.assertEqual(site['o:id'], 2)
        self.assertEqual(site['o:slug'], 'site2')
        self.assertEqual(site['o:title'], 'Site 2')
        
        # Check the mock was called correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'GET')
        self.assertEqual(kwargs['url'], 'http://example.com/api/sites')
        self.assertEqual(kwargs['headers'], {'Content-Type': 'application/json'})
    
    @patch('src.Omeka.OmekaAdapter.requests.request')
    def test_get_site_by_slug_not_found(self, mock_request):
        """Test getting a site by slug when not found."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'o:id': 1,
                'o:slug': 'site1',
                'o:title': 'Site 1'
            },
            {
                'o:id': 2,
                'o:slug': 'site2',
                'o:title': 'Site 2'
            }
        ]
        mock_request.return_value = mock_response
        
        # Call the method
        site = self.adapter.get_site_by_slug('site3')
        
        # Check the result
        self.assertIsNone(site)
        
        # Check the mock was called correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'GET')
        self.assertEqual(kwargs['url'], 'http://example.com/api/sites')
        self.assertEqual(kwargs['headers'], {'Content-Type': 'application/json'})

if __name__ == '__main__':
    unittest.main()
