#!/usr/bin/env python3

"""
Omeka Adapter Module

This module provides functionality to interact with the Omeka S API.

Author: [Your Name]
Date: 23-07-2025
"""

import json
import logging
import os
import requests
from typing import Dict, Any, List, Optional

class OmekaAdapter:
    """Class to interact with the Omeka S API."""
    
    def __init__(self, api_url: str, key_identity: Optional[str] = None, key_credential: Optional[str] = None, 
                 logger: Optional[logging.Logger] = None):
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
        self.logger = logger or logging.getLogger(__name__)
    
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
        
        if response.status_code in [200,201,202,204]:
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
            "o:is_active": True,
            "limit_to_granted_sites": True,
            "limit_to_own_assets": True
        }
        
        self.logger.debug(f"Creating user: {name} with email: {email} and role: {role}")
        response = self._make_request("POST", endpoint, data)
        
        if response.status_code in [200,201,202,204]:
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
        response = self._make_request("GET", endpoint, params={})
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
            self.logger.info(f"User (ID: {user_id}) added to site (ID: {site_id}) successfully")
            return site_data
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
        
        if response.status_code in [200,201,202,204]:
            job_data = response.json()
            self.logger.info(f"Job created successfully: {job_class} (ID: {job_data['o:id']})")
            return job_data
        else:
            self.logger.error(f"Failed to create job: {job_class}. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def create_bulk_importer(self, importer_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new bulk importer in Omeka S.
        
        Args:
            importer_config: The configuration for the importer.
            
        Returns:
            The created bulk importer data.
        """
        endpoint = f"{self.api_url}/bulk_importers"
        
        self.logger.debug(f"Creating bulk importer: {importer_config.get('o:label', 'Unknown')}")
        response = self._make_request("POST", endpoint, importer_config)
        
        if response.status_code in [200,201,202,204]:
            importer_data = response.json()
            self.logger.info(f"Bulk importer created successfully: {importer_data.get('o:label')} (ID: {importer_data['o:id']})")
            return importer_data
        else:
            self.logger.error(f"Failed to create bulk importer. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def create_bulk_import(self, importer_id: int, xml_file: str, site_name: str, owner_id: int = None, site_id: int = None) -> Dict[str, Any]:
        """
        Create a new bulk import job in Omeka S.
        
        Args:
            importer_id: The ID of the importer to use.
            xml_file: The path to the XML file to import.
            site_name: The name of the site for the comment.
            owner_id: The ID of the owner for the imported resources (optional).
            site_id: The ID of the site for the SiteId parameter in xsl_params (optional).
            
        Returns:
            The created bulk import job data.
        """
        endpoint = f"{self.api_url}/bulk_imports"
        
        # Get the importer to determine its label and configuration
        importer_endpoint = f"{self.api_url}/bulk_importers/{importer_id}"
        importer_response = self._make_request("GET", importer_endpoint, params={})
        
        if importer_response.status_code != 200:
            self.logger.error(f"Failed to get importer. Importer ID: {importer_id}. Status code: {importer_response.status_code}")
            self.logger.error(f"Response: {importer_response.text}")
            importer_response.raise_for_status()
        
        importer_data = importer_response.json()
        importer_label = importer_data.get("o:label", "Unknown Importer")
        importer_config = importer_data.get("o:config", {})
        
        # Get file information
        file_name = os.path.basename(xml_file)
        file_size = os.path.getsize(xml_file)
        
        # Start with the importer's configuration
        reader_config = importer_config.get("reader", {}).copy() if importer_config.get("reader") else {}
        processor_config = importer_config.get("processor", {}).copy() if importer_config.get("processor") else {}
        
        # Update reader configuration with file information
        reader_config.update({
            "filename": f"/var/www/html/omeka-s/files/preload/{file_name}",
            "file": {
                "name": file_name,
                "full_path": file_name,
                "type": "text/xml",
                "error": 0,
                "size": file_size
            }
        })
        self.logger.info(f"FILENAME: {reader_config['filename']}")
        
        # Update SiteId parameter in xsl_params if provided
        if site_id is not None and "xsl_params" in reader_config and "SiteId" in reader_config["xsl_params"]:
            self.logger.info(f"Setting SiteId parameter to '{site_id}' for import job")
            reader_config["xsl_params"]["SiteId"] = str(site_id)
        
        # Update processor configuration with owner information
        if owner_id:
            processor_config["o:owner"] = owner_id
        
        # Create import configuration
        import_config = {
            "@type": "o-bulk:Import",
            "o:job": None,
            "o-bulk:comment": f"Site: {site_name},Importer: {importer_label}",
            "o:status": "ready",
            "o:undo_job": None,
            "o:importer": importer_id,
            "o:params": {
                "reader": reader_config,
                "mapping": None,
                "processor": processor_config
            }
        }
        
        self.logger.debug(f"Creating bulk import job for importer ID: {importer_id}")
        response = self._make_request("POST", endpoint, import_config)
        
        if response.status_code in [200,201,202,204]:
            import_data = response.json()
            self.logger.info(f"Bulk import job created successfully: (ID: {import_data['o:id']})")
            return import_data
        else:
            self.logger.error(f"Failed to create bulk import job. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def get_bulk_importer_by_label(self, label: str) -> Optional[Dict[str, Any]]:
        """
        Get a bulk importer by its label.
        
        Args:
            label: The label of the bulk importer.
            
        Returns:
            The bulk importer data or None if not found.
        """
        endpoint = f"{self.api_url}/bulk_importers"
        
        self.logger.debug(f"Getting bulk importer by label: {label}")
        params = {"label": label}
        response = self._make_request("GET", endpoint, params=params)
        
        if response.status_code == 200:
            importers = response.json()
            for importer in importers:
                if importer.get("o:label") == label:
                    self.logger.info(f"Found bulk importer with label: {label} (ID: {importer['o:id']})")
                    return importer
            
            self.logger.warning(f"Bulk importer with label: {label} not found")
            return None
        else:
            self.logger.error(f"Failed to get bulk importers. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def get_bulk_mapping_by_label(self, label: str) -> Optional[Dict[str, Any]]:
        """
        Get a bulk mapping by its label.
        
        Args:
            label: The label of the bulk mapping.
            
        Returns:
            The bulk mapping data or None if not found.
        """
        endpoint = f"{self.api_url}/bulk_mappings"
        
        self.logger.debug(f"Getting bulk mapping by label: {label}")
        params = {"label": label}
        response = self._make_request("GET", endpoint, params=params)
        
        if response.status_code == 200:
            mappings = response.json()
            for mapping in mappings:
                if mapping.get("o:label") == label:
                    self.logger.info(f"Found bulk mapping with label: {label} (ID: {mapping['o:id']})")
                    return mapping
            
            self.logger.warning(f"Bulk mapping with label: {label} not found")
            return None
        else:
            self.logger.error(f"Failed to get bulk mappings. Status code: {response.status_code}")
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
        
        self.logger.info(f"Getting site by slug: {slug}")
        params = {"slug": slug}
        response = self._make_request("GET", endpoint, params=params)
        
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
        params = {"email": email}
        response = self._make_request("GET", endpoint, params=params)
        
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
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> requests.Response:
        """
        Make a request to the Omeka S API.
        
        Args:
            method: The HTTP method (GET, POST, PUT, DELETE).
            endpoint: The API endpoint.
            data: The data to send (optional).
            params: Additional query parameters to include in the request (optional).
            
        Returns:
            The response from the API.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Initialize params if not provided
        if params is None:
            params = {}
        
        # Add authentication headers if provided
        if self.key_identity and self.key_credential:
            params.update({
                "key_identity": self.key_identity,
                "key_credential": self.key_credential
            })
        
        if data:
            data_json = json.dumps(data)
        else:
            data_json = None
        
        response = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            params=params,
            data=data_json
        )
        
        return response
