#!/usr/bin/env python3

"""
JSON Reporter Module

This module provides functionality to generate a JSON report of the migration process.

Author: [Your Name]
Date: 26-08-2025
"""

import json
import os
import re
import logging
from typing import Dict, Any, List, Optional

class JSONReporter:
    """Class to generate a JSON report of the migration process."""
    
    def __init__(self, output_file: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the JSON reporter.
        
        Args:
            output_file: The path to the output JSON file.
            logger: A logger instance (optional).
        """
        self.output_file = output_file
        self.logger = logger or logging.getLogger(__name__)
        self.report_data = []
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Initialize the file if it doesn't exist
        if not os.path.exists(output_file):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def count_xml_tags(self, xml_file: str) -> Dict[str, int]:
        """
        Count occurrences of specific XML tags in the given file.
        
        Args:
            xml_file: The path to the XML file.
            
        Returns:
            A dictionary with the tag counts.
        """
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                xml_text = f.read()
            
            attachment_root_items = 0
            attachment_items = 0
            
            # Find all <item> blocks
            item_pattern = r'<item\b[^>]*>.*?</item>'
            item_blocks = re.findall(item_pattern, xml_text, flags=re.IGNORECASE | re.DOTALL)
            
            for item_block in item_blocks:
                # Check if this item has wp:post_type with attachment (handle CDATA)
                post_type_pattern = r'<wp:post_type\b[^>]*>\s*(?:<!\[CDATA\[)?\s*attachment\s*(?:\]\]>)?\s*</wp:post_type>'
                if re.search(post_type_pattern, item_block, flags=re.IGNORECASE):
                    attachment_items += 1
                    
                    # Also check if wp:post_parent=0 (no CDATA for numbers)
                    post_parent_pattern = r'<wp:post_parent\b[^>]*>\s*0\s*</wp:post_parent>'
                    if re.search(post_parent_pattern, item_block, flags=re.IGNORECASE):
                        attachment_root_items += 1
            
            # Count wp:term_taxonomy with media-category (exact CDATA format)
            media_category_pattern = r'<wp:term_taxonomy\b[^>]*>\s*<!\[CDATA\[media-category\]\]>\s*</wp:term_taxonomy>'
            media_category_matches = re.findall(media_category_pattern, xml_text, flags=re.IGNORECASE | re.DOTALL)
            media_category_terms = len(media_category_matches)
            
            return {
                'number_of_itemsets': media_category_terms,
                'number_of_items': attachment_root_items,
                'number_of_media': attachment_items
            }
        except Exception as e:
            self.logger.error(f"Error counting XML tags in {xml_file}: {str(e)}")
            return {
                'number_of_itemsets': 0,
                'number_of_items': 0,
                'number_of_media': 0
            }
    
    def add_channel_report(self, channel_data: Dict[str, Any], migration_result: Dict[str, Any]) -> None:
        """
        Add a channel migration report to the JSON file.
        
        Args:
            channel_data: The channel data from the CSV file.
            migration_result: The result of the migration process.
        """
        # Extract required information
        site = migration_result.get('site', {})
        user = migration_result.get('user', {})
        xml_file = migration_result.get('xml_file', '')
        import_jobs = migration_result.get('import_jobs', [])
        
        # Count XML tags
        tag_counts = self.count_xml_tags(xml_file)
        
        # Create report entry
        report_entry = {
            'name': channel_data.get('name', ''),
            'url': channel_data.get('url', ''),
            'slug': channel_data.get('slug', ''),
            'editor': channel_data.get('editor', ''),
            'site_id': site.get('o:id', ''),
            'user_id': user.get('o:id', ''),
            'user_login': user.get('o:name', ''),
            'tasks_created': [
                {
                    'importer': self._get_importer_label(job, migration_result.get('importers', [])), 
                    'id': job.get('o:id', '')
                }
                for job in import_jobs
            ],
            'number_of_itemsets': tag_counts['number_of_itemsets'],
            'number_of_items': tag_counts['number_of_items'],
            'number_of_media': tag_counts['number_of_media']
        }
        
        # Read existing data
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = []
        
        # Add new entry
        existing_data.append(report_entry)
        
        # Write updated data
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Added report for channel {channel_data.get('name')} to {self.output_file}")
    
    def _get_importer_label(self, job: Dict[str, Any], importers: List[Dict[str, Any]]) -> str:
        """
        Get the importer label for a job.
        
        Args:
            job: The job data.
            importers: List of importers.
            
        Returns:
            The importer label.
        """
        # First try to get the importer label from the job itself
        if 'o-bulk:importer' in job and isinstance(job['o-bulk:importer'], dict) and 'o:label' in job['o-bulk:importer']:
            return job['o-bulk:importer']['o:label']
        
        # If not found, try to get it from the comment field
        if 'o-bulk:comment' in job:
            comment = job.get('o-bulk:comment', '')
            if 'Importer:' in comment:
                importer_part = comment.split('Importer:')[1].strip()
                if ',' in importer_part:
                    return importer_part.split(',')[0].strip()
                return importer_part
        
        # If not found, try to get it from the importers list
        importer_id = job.get('o:importer')
        if importer_id and importers:
            for importer in importers:
                if importer.get('o:id') == importer_id:
                    return importer.get('o:label', '')
        
        # If all else fails, try to get it from the config
        try:
            with open('migration_config.json', 'r') as f:
                config = json.load(f)
                importers_config = config.get('importers', [])
                for importer_config in importers_config:
                    if 'o:id' in importer_config and importer_config['o:id'] == importer_id:
                        return importer_config.get('o:label', '')
        except Exception:
            pass
        
        # If still not found, return a default label based on the job ID
        return f"Importer {job.get('o:id', 'Unknown')}"
