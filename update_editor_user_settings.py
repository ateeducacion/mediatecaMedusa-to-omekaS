#!/usr/bin/env python3

"""
Update User Settings Script

This script updates specific user settings for all users with the 'editor' role in Omeka S.
It sets the following settings:
- "o-module-isolatedsites:limit_to_granted_sites": true
- "o-module-isolatedsites:limit_to_own_assets": true

Author: Generated Script
Date: 29-09-2025
"""

import json
import logging
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.Omeka.OmekaAdapter import OmekaAdapter
from src.logger import setup_logger


class UserSettingsUpdater:
    """Class to update user settings in Omeka S."""
    
    def __init__(self, api_url: str, key_identity: str, key_credential: str, 
                 logger: Optional[logging.Logger] = None):
        """
        Initialize the user settings updater.
        
        Args:
            api_url: The URL of the Omeka S API.
            key_identity: The identity key for API authentication.
            key_credential: The credential key for API authentication.
            logger: Optional logger instance.
        """
        self.omeka_adapter = OmekaAdapter(api_url, key_identity, key_credential, logger)
        self.logger = logger or logging.getLogger(__name__)
        
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users from Omeka S.
        
        Returns:
            List of all users.
        """
        endpoint = f"{self.omeka_adapter.api_url}/users"
        
        self.logger.info("Fetching all users from Omeka S")
        response = self.omeka_adapter._make_request("GET", endpoint, params={})
        
        if response.status_code == 200:
            users = response.json()
            self.logger.info(f"Found {len(users)} users")
            return users
        else:
            self.logger.error(f"Failed to get users. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        Get all users with a specific role.
        
        Args:
            role: The role to filter by.
            
        Returns:
            List of users with the specified role.
        """
        all_users = self.get_all_users()
        editor_users = [user for user in all_users if user.get('o:role') == role]
        
        self.logger.info(f"Found {len(editor_users)} users with role '{role}'")
        return editor_users
    
    def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user settings in Omeka S.
        
        Args:
            user_id: The ID of the user to update.
            settings: Dictionary of settings to update.
            
        Returns:
            The updated user data.
        """
        endpoint = f"{self.omeka_adapter.api_url}/users/{user_id}"
        
        # First, get the current user data
        self.logger.debug(f"Getting current data for user ID: {user_id}")
        response = self.omeka_adapter._make_request("GET", endpoint, params={})
        
        if response.status_code != 200:
            self.logger.error(f"Failed to get user data. User ID: {user_id}. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
        
        user_data = response.json()
        
        # Update the user data with new settings
        user_data.update(settings)
        
        # Update the user
        self.logger.debug(f"Updating settings for user ID: {user_id}")
        response = self.omeka_adapter._make_request("PUT", endpoint, user_data)
        
        if response.status_code == 200:
            updated_user = response.json()
            self.logger.info(f"Successfully updated settings for user ID: {user_id} ({user_data.get('o:name', 'Unknown')})")
            return updated_user
        else:
            self.logger.error(f"Failed to update user settings. User ID: {user_id}. Status code: {response.status_code}")
            self.logger.error(f"Response: {response.text}")
            response.raise_for_status()
    
    def update_editor_users_settings(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Update settings for all users with 'editor' role.
        
        Args:
            dry_run: If True, only show what would be updated without making changes.
            
        Returns:
            Dictionary with update results.
        """
        # Settings to apply
        settings_to_update = {
            "o-module-isolatedsites:limit_to_granted_sites": True,
            "o-module-isolatedsites:limit_to_own_assets": True
        }
        
        # Get all editor users
        editor_users = self.get_users_by_role('editor')
        
        if not editor_users:
            self.logger.warning("No users with 'editor' role found")
            return {"updated": 0, "errors": 0, "users": []}
        
        results = {
            "updated": 0,
            "errors": 0,
            "users": []
        }
        
        self.logger.info(f"{'DRY RUN: ' if dry_run else ''}Updating settings for {len(editor_users)} editor users")
        
        for user in editor_users:
            user_id = user.get('o:id')
            user_name = user.get('o:name', 'Unknown')
            user_email = user.get('o:email', 'Unknown')
            
            try:
                if dry_run:
                    self.logger.info(f"DRY RUN: Would update user ID: {user_id} ({user_name} - {user_email})")
                    self.logger.info(f"DRY RUN: Settings to apply: {settings_to_update}")
                    results["users"].append({
                        "id": user_id,
                        "name": user_name,
                        "email": user_email,
                        "status": "would_update"
                    })
                else:
                    updated_user = self.update_user_settings(user_id, settings_to_update)
                    results["updated"] += 1
                    results["users"].append({
                        "id": user_id,
                        "name": user_name,
                        "email": user_email,
                        "status": "updated"
                    })
                    
            except Exception as e:
                self.logger.error(f"Error updating user ID: {user_id} ({user_name}): {str(e)}")
                results["errors"] += 1
                results["users"].append({
                    "id": user_id,
                    "name": user_name,
                    "email": user_email,
                    "status": "error",
                    "error": str(e)
                })
        
        return results


def main():
    """Main function to run the user settings update."""
    parser = argparse.ArgumentParser(description='Update user settings for editor users in Omeka S')
    parser.add_argument('--api-url', required=True, help='Omeka S API URL')
    parser.add_argument('--key-identity', required=True, help='API key identity')
    parser.add_argument('--key-credential', required=True, help='API key credential')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       help='Set the logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger(log_level=args.log_level)
    
    try:
        # Initialize the updater
        updater = UserSettingsUpdater(
            api_url=args.api_url,
            key_identity=args.key_identity,
            key_credential=args.key_credential,
            logger=logger
        )
        
        # Update editor users settings
        results = updater.update_editor_users_settings(dry_run=args.dry_run)
        
        # Print summary
        logger.info("=" * 50)
        logger.info("UPDATE SUMMARY")
        logger.info("=" * 50)
        
        if args.dry_run:
            logger.info(f"DRY RUN: Would update {len([u for u in results['users'] if u['status'] == 'would_update'])} users")
        else:
            logger.info(f"Successfully updated: {results['updated']} users")
            logger.info(f"Errors: {results['errors']} users")
        
        # Print detailed results
        for user in results['users']:
            status_msg = f"User ID: {user['id']} ({user['name']} - {user['email']}) - Status: {user['status']}"
            if user.get('error'):
                status_msg += f" - Error: {user['error']}"
            logger.info(status_msg)
        
        # Save results to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"user_settings_update_results_{'dry_run_' if args.dry_run else ''}{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to: {results_file}")
        
        if results['errors'] > 0:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Script failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
