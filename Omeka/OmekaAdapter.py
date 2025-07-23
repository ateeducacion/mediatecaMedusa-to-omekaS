#!/usr/bin/env python3

"""
Omeka Adapter Module

This module provides functionality to interact with the Omeka S API.

Author: [Your Name]
Date: 23-07-2025
"""

import json
import logging
import requests
from typing import Dict, Any, List, Optional

class OmekaAdapter:
    """Class to interact with the Omeka S API."""
    
    def __init__(self, api_url: str, key_identity: Optional[str] = None, key_credential: Optional[str] = None):
        """
        Initialize the Omeka adapter.
        
        Args:
            api_url: The URL of the Omeka S API.
            key_identity: The identity key for API authentication (optional).
            key_credential: The credential key for API authentication (optional).
        """
        self.api_url = api_url.rstrip('/')
        self.key_identity = key_identity
        self.key_credential = key_credential
        self.logger = logging.getLogger(__name__)
    
    def create_site(self, name: str, slug: str) -> Dict[str, Any]:
        """
        Create a new site in Omeka S.
        
        Args:
            name: The name of the site.
            slug: The slug of the site.
            
        Returns:
            The created site data.
        """
        endpoint = f"{self.api_url}/sites"
        
        data = {
            "o:title": name,
            "o:slug": slug,
            "o:theme": "freedom",
            "o:is_public": True,
            "o:assign_new_items": False,
            "o:owner": {"o:id": 1}
        }
        
        self.logger.debug(f"Creating site: {name} with slug: {slug}")
        response = self._make_request("POST", endpoint, data)
        
        if response.status_code == 201:
            site_data = response.json()
            self.logger.info(f"Site created successfully: {name} (ID: {site_data['o:id']})")
            return site_data
        else:
            self.logger.error(f"Failed to create site: {name}. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def create_user(self, name: str, email: str, role: str = "editor") -> Dict[str, Any]:
        """
        Create a new user in Omeka S.
        
        Args:
            name: The name of the user.
            email: The email of the user.
            role: The role of the user (default: editor).
            
        Returns:
            The created user data.
        """
        endpoint = f"{self.api_url}/users"
        
        data = {
            "o:name": name,
            "o:email": email,
            "o:role": role,
            "o:is_active": True
        }
        
        self.logger.debug(f"Creating user: {name} with email: {email} and role: {role}")
        response = self._make_request("POST", endpoint, data)
        
        if response.status_code == 201:
            user_data = response.json()
            self.logger.info(f"User created successfully: {name} (ID: {user_data['o:id']})")
            return user_data
        else:
            self.logger.error(f"Failed to create user: {name}. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def add_user_to_site(self, site_id: int, user_id: int, role: str = "viewer") -> Dict[str, Any]:
        """
        Add a user to a site in Omeka S.
        
        Args:
            site_id: The ID of the site.
            user_id: The ID of the user.
            role: The role of the user in the site (default: viewer).
            
        Returns:
            The updated site data.
        """
        endpoint = f"{self.api_url}/sites/{site_id}"
        
        # First, get the current site data
        response = self._make_request("GET", endpoint)
        
        if response.status_code != 200:
            self.logger.error(f"Failed to get site data. Site ID: {site_id}. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
        
        site_data = response.json()
        
        # Add the user to the site permissions
        site_permissions = site_data.get("o:site_permission", [])
        
        # Check if the user is already in the site permissions
        for permission in site_permissions:
            if permission["o:user"]["o:id"] == user_id:
                self.logger.warning(f"User (ID: {user_id}) already has permissions for site (ID: {site_id})")
                return site_data
        
        # Add the user to the site permissions
        site_permissions.append({
            "o:user": {"o:id": user_id},
            "o:role": role
        })
        
        site_data["o:site_permission"] = site_permissions
        
        # Update the site
        self.logger.debug(f"Adding user (ID: {user_id}) to site (ID: {site_id}) with role: {role}")
        response = self._make_request("PUT", endpoint, site_data)
        
        if response.status_code == 200:
            updated_site_data = response.json()
            self.logger.info(f"User (ID: {user_id}) added to site (ID: {site_id}) successfully")
            return updated_site_data
        else:
            self.logger.error(f"Failed to add user to site. Site ID: {site_id}, User ID: {user_id}. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def create_job(self, job_class: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new job in Omeka S.
        
        Args:
            job_class: The class of the job.
            args: The arguments for the job (optional).
            
        Returns:
            The created job data.
        """
        endpoint = f"{self.api_url}/jobs"
        
        data = {
            "o:class": job_class
        }
        
        if args:
            data["o:args"] = args
        
        self.logger.debug(f"Creating job: {job_class} with args: {args}")
        response = self._make_request("POST", endpoint, data)
        
        if response.status_code == 201:
            job_data = response.json()
            self.logger.info(f"Job created successfully: {job_class} (ID: {job_data['o:id']})")
            return job_data
        else:
            self.logger.error(f"Failed to create job: {job_class}. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def get_site_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get a site by its slug.
        
        Args:
            slug: The slug of the site.
            
        Returns:
            The site data or None if not found.
        """
        endpoint = f"{self.api_url}/sites"
        
        self.logger.debug(f"Getting site by slug: {slug}")
        response = self._make_request("GET", endpoint)
        
        if response.status_code == 200:
            sites = response.json()
            for site in sites:
                if site.get("o:slug") == slug:
                    self.logger.info(f"Found site with slug: {slug} (ID: {site['o:id']})")
                    return site
            
            self.logger.warning(f"Site with slug: {slug} not found")
            return None
        else:
            self.logger.error(f"Failed to get sites. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by its email.
        
        Args:
            email: The email of the user.
            
        Returns:
            The user data or None if not found.
        """
        endpoint = f"{self.api_url}/users"
        
        self.logger.debug(f"Getting user by email: {email}")
        response = self._make_request("GET", endpoint)
        
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if user.get("o:email") == email:
                    self.logger.info(f"Found user with email: {email} (ID: {user['o:id']})")
                    return user
            
            self.logger.warning(f"User with email: {email} not found")
            return None
        else:
            self.logger.error(f"Failed to get users. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> requests.Response:
        """
        Make a request to the Omeka S API.
        
        Args:
            method: The HTTP method (GET, POST, PUT, DELETE).
            endpoint: The API endpoint.
            data: The data to send (optional).
            
        Returns:
            The response from the API.
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add authentication headers if provided
        if self.key_identity and self.key_credential:
            headers["X-Api-Key"] = self.key_identity
            headers["X-Api-Credential"] = self.key_credential
        
        if data:
            data_json = json.dumps(data)
        else:
            data_json = None
        
        response = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            data=data_json
        )
        
        return response
