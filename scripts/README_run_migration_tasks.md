# Run Migration Tasks Script

This PHP script is designed to execute bulk import tasks for Omeka S migrations based on a JSON input file. It reads the task information, executes each task, and updates the JSON with job IDs and additional information.

## Overview

The script is part of a larger WordPress to Omeka S migration tool. It's specifically designed to handle the execution of bulk import tasks that were previously created during the migration process. The script:

1. Reads a JSON file containing information about migrated channels and their associated bulk import tasks
2. Executes each bulk import task using the EasyAdmin module's task.php script
3. Captures the job ID for each executed task and identifies the new bulk import task created for the job
4. Retrieves item sets, items, and media counts for each site using the Omeka S API
5. Adds item sets with dcterms:subject matching the site ID to the site and clears the subject field
6. Adds the site to the channel editor's `default_item_sites` user setting
7. Optionally applies site configuration (theme, site settings, theme settings) from a JSON file
8. Optionally configures default navigation with a redirect page as homepage
9. Updates the JSON with the job IDs, new task IDs, and counts
10. Optionally deletes the original tasks
11. Writes the updated information to an output JSON file (incrementally, channel by channel)

## Requirements

- PHP 7.4 or higher
- Omeka S installation with the following modules:
  - EasyAdmin
  - BulkImport
- Access to the Omeka S file system and database

## Usage

```bash
php run_migration_tasks.php --input-file <input_file> --output-file <output_file> [--delete-tasks] [--omeka-path <path>] [--config-site-file <config_file>] [--default-nav] [--base-url <url>]
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `--input-file` | Yes | Path to the input JSON file with migration tasks information |
| `--output-file` | Yes | Path to the output JSON file to write the updated information |
| `--delete-tasks` | No | Delete the original tasks after execution |
| `--omeka-path` | No | Path to the Omeka S installation (default: `/var/www/html`) |
| `--config-site-file` | No | Path to a JSON file with site settings to apply to all sites |
| `--default-nav` | No | Configure default navigation for all sites |
| `--base-url` | No | Base URL of the Omeka installation (used with `--default-nav`, e.g., `http://localhost:8888`) |

### Docker Example

```bash
docker exec -it omeka-s-docker-omekas-1 php run_migration_tasks.php \
  --input-file /path/to/input.json \
  --output-file /path/to/output.json \
  --delete-tasks \
  --config-site-file /path/to/site_conf.json \
  --default-nav \
  --base-url http://localhost:8888
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
    "omeka_items_count": 12,
    "omeka_media_count": 5
  }
]
```

The added fields are:
- `job_id` in each task: The ID of the job created by the task.php script
- `new_task_id` in each task: The ID of the new bulk import task created for the job
- `omeka_itemsets_count`: The number of item sets in the Omeka S site
- `omeka_items_count`: The number of items in the Omeka S site
- `omeka_media_count`: The number of media files in the Omeka S site

## Error Handling

The script includes error handling for various scenarios:
- Missing or invalid input file
- Missing or invalid config site file
- Failed task execution
- Failed task deletion
- Failed retrieval of new task IDs
- Failed item counts retrieval
- Failed item set assignment to sites
- Failed user default_item_sites update
- Failed site configuration application
- Failed navigation configuration

## Item Sets Assignment

The script automatically assigns item sets to sites based on the dcterms:subject field:

1. After executing all tasks for a channel, the script searches for item sets with dcterms:subject matching the site ID
2. Item sets with no items are deleted instead of being added to the site
3. For non-empty item sets, the dcterms:subject field is cleared to prevent duplicate assignments
4. The item sets are added to the site's `o:site_item_set` field, making them visible in the site

### Admin User Authentication

To avoid permission issues, the script uses the admin user (ID 1) for API operations:

1. The script authenticates as the admin user at startup
2. All API operations are performed with admin privileges

All errors are logged to the console with detailed information.

## User Default Item Sites

After processing item sets, the script adds the site to the channel editor's `default_item_sites` user setting:

- Reads the current `default_item_sites` array for the user
- Adds the `site_id` if not already present (no duplicates)
- Uses the `Omeka\Settings\User` service for persistence

## Site Configuration (`--config-site-file`)

If a config file is provided, the script applies the following to every processed site:

1. **Theme** — Sets `o:theme` via the API
2. **Site settings** — Applies each key/value pair under `site_settings` using `Omeka\Settings\Site`
3. **Theme settings** — Applies settings stored under keys prefixed `theme_settings_<theme-name>`

### Config file format

```json
{
  "site_data": {
    "site": {
      "theme": "freedom-ate"
    },
    "site_settings": {
      "item_set_page_title": "",
      "browse_heading_property_term": "dcterms:title"
    },
    "theme_settings_freedom-ate": {
      "freedom-ate_browse_layout": "grid",
      "freedom-ate_resource_tags": false
    }
  }
}
```

## Default Navigation (`--default-nav`)

When `--default-nav` is passed, the script configures a default navigation for each site:

1. Creates (or updates) a site page with slug `item` and title `Inicio` that contains a `redirectToUrl` block pointing to `<base-url>/s/<site-slug>/item`
2. Sets this page as the site homepage (`o:homepage`)
3. Adds two navigation entries:
   - The redirect page (unlabelled, used as homepage redirect)
   - A `browseItemSets` link labelled `Colecciones`

> **Note:** `--base-url` should be provided together with `--default-nav`. If omitted, `http://localhost:8888` is used and a warning is printed.

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
- The script writes output incrementally after each channel to avoid data loss if interrupted.
- The script automatically identifies and records the new bulk import tasks created for each job.
- Item sets with dcterms:subject matching the site ID are automatically added to the site and the subject field is cleared. Empty item sets are deleted.
- The script uses the admin user (ID 1) for API operations to ensure it has sufficient permissions.
