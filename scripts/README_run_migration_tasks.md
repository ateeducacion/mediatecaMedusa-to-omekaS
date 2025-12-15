# Run Migration Tasks Script

This PHP script is designed to execute bulk import tasks for Omeka S migrations based on a JSON input file. It reads the task information, executes each task, and updates the JSON with job IDs and additional information.

## Overview

The script is part of a larger WordPress to Omeka S migration tool. It's specifically designed to handle the execution of bulk import tasks that were previously created during the migration process. The script:

1. Reads a JSON file containing information about migrated channels and their associated bulk import tasks
2. Executes each bulk import task using the EasyAdmin module's task.php script
3. Captures the job ID for each executed task and identifies the new bulk import task created for the job
4. Retrieves item sets and items counts for each site using the Omeka S API
5. Adds item sets with dcterms:subject matching the site ID to the site and clears the subject field
6. Updates the JSON with the job IDs, new task IDs, and counts
7. Optionally deletes the original tasks
8. Writes the updated information to an output JSON file

## Requirements

- PHP 7.4 or higher
- Omeka S installation with the following modules:
  - EasyAdmin
  - BulkImport
- Access to the Omeka S file system and database

## Usage

```bash
php run_migration_tasks.php --input-file <input_file> --output-file <output_file> [--delete-tasks] [--omeka-path <path>]
```

### Arguments

- `--input-file`: Path to the input JSON file with migration tasks information
- `--output-file`: Path to the output JSON file to write the updated information
- `--delete-tasks`: (Optional) Delete the original tasks after execution
- `--omeka-path`: (Optional) Path to the Omeka S installation (default: /var/www/html)

### Docker Example

If you're using Docker, you can run the script with:

```bash
docker exec -it omeka-s-docker-omekas-1 php run_migration_tasks.php --input-file /path/to/input.json --output-file /path/to/output.json --delete-tasks
```

## Input JSON Format

The input JSON file should have the following structure:

```json
[
  {
    "name": "Channel Name",
    "url": "https://example.com/channel",
    "slug": "channel-slug",
    "editor": "editor_username",
    "site_id": 123,
    "user_id": 456,
    "user_login": "editor_username",
    "tasks_created": [
      {
        "importer": "T0. WP categories to Item Set XML",
        "id": 789
      },
      {
        "importer": "T1. WP posts to Items XML",
        "id": 790
      },
      {
        "importer": "T2. WP attachments to Media XML",
        "id": 791
      }
    ],
    "number_of_itemsets": 86,
    "number_of_items": 12,
    "number_of_media": 12
  }
]
```

## Output JSON Format

The output JSON file will have the same structure as the input file, but with additional information:

```json
[
  {
    "name": "Channel Name",
    "url": "https://example.com/channel",
    "slug": "channel-slug",
    "editor": "editor_username",
    "site_id": 123,
    "user_id": 456,
    "user_login": "editor_username",
    "tasks_created": [
      {
        "importer": "T0. WP categories to Item Set XML",
        "id": 789,
        "job_id": "1001",
        "new_task_id": 1101
      },
      {
        "importer": "T1. WP posts to Items XML",
        "id": 790,
        "job_id": "1002",
        "new_task_id": 1102
      },
      {
        "importer": "T2. WP attachments to Media XML",
        "id": 791,
        "job_id": "1003",
        "new_task_id": 1103
      }
    ],
    "number_of_itemsets": 86,
    "number_of_items": 12,
    "number_of_media": 12,
    "omeka_itemsets_count": 86,
    "omeka_items_count": 12
  }
]
```

The added fields are:
- `job_id` in each task: The ID of the job created by the task.php script
- `new_task_id` in each task: The ID of the new bulk import task created for the job
- `omeka_itemsets_count`: The number of item sets in the Omeka S site
- `omeka_items_count`: The number of items in the Omeka S site

## Error Handling

The script includes error handling for various scenarios:
- Missing or invalid input file
- Failed task execution
- Failed task deletion
- Failed retrieval of new task IDs
- Failed item counts retrieval
- Failed item set assignment to sites

## Item Sets Assignment

The script automatically assigns item sets to sites based on the dcterms:subject field:

1. After executing all tasks for a channel, the script searches for item sets with dcterms:subject matching the site ID
2. These item sets are added to the site's o:site_item_set field, making them visible in the site
3. The dcterms:subject field is then cleared from these item sets to prevent duplicate assignments
4. Finally, empty item sets 

This process ensures that item sets created during the import process are properly associated with their respective sites.

### Admin User Authentication

To avoid permission issues, the script uses the admin user (ID 1) for API operations:

1. The script authenticates as the admin user at startup
2. All API operations are performed with admin privileges
3. This ensures that the script has sufficient permissions to:
   - Find item sets with dcterms:subject matching the site ID
   - Add these item sets to the site
   - Clear the dcterms:subject field from these item sets

All errors are logged to the console with detailed information.

## Integration with Migration Process

This script is designed to be used after the initial migration process has created the bulk import tasks. The typical workflow is:

1. Run the WordPress to Omeka S migration tool to create sites, users, and bulk import tasks
2. Use the JSON output file from the migration tool as input for this script
3. Run this script to execute the bulk import tasks and update the JSON with job IDs and counts
4. Use the updated JSON for reporting and monitoring the migration process

## Notes

- The script uses the Omeka S API to retrieve item counts, so it needs to be run on a server with access to the Omeka S installation.
- The script executes tasks sequentially, which may take a long time for a large number of tasks.
- The `--delete-tasks` option will permanently delete the original bulk import tasks after execution. Use this option with caution.
- The script automatically identifies and records the new bulk import tasks created for each job, which can be used for future reference or cleanup.
- Item sets with dcterms:subject matching the site ID are automatically added to the site and the subject field is cleared.
- The script uses the admin user (ID 1) for API operations to ensure it has sufficient permissions.
- The admin user must exist in the Omeka S installation for the script to work properly.


## Site configuration

1. Site settings

2. Theme settings