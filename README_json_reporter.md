# JSON Reporter for WordPress to Omeka S Migration

This document describes the JSON reporter functionality added to the WordPress to Omeka S migration tool.

## Overview

The JSON reporter generates a JSON file with information about each channel migrated from WordPress to Omeka S. The report includes details such as:

- Channel information (name, URL, slug, editor)
- Site and user IDs in Omeka S
- Tasks created for the migration
- Statistics about the content (number of itemsets, items, and media)

## Usage

### Command Line Arguments

The JSON reporter is activated by adding the `--output-file` parameter to the migration command:

```bash
python main.py --csv <csv_file> --omeka-url <omeka_url> --wp-username <username> --wp-password <password> --key-identity <key_identity> --key-credential <key_credential> --config <config_file> --output-file <output_file>
```

For test migrations:

```bash
python run_test_migration.py --omeka-url <omeka_url> --wp-username <username> --wp-password <password> --key-identity <key_identity> --key-credential <key_credential> --channel-url <channel_url> --output-file <output_file>
```

### Output Format

The output file is a JSON array where each element represents a migrated channel. Here's an example of the JSON structure:

```json
[
  {
    "name": "Channel Name",
    "url": "https://example.com/channel",
    "slug": "channel-name",
    "editor": "editor_username",
    "site_id": 123,
    "user_id": 456,
    "user_login": "editor_username",
    "tasks_created": [
      {
        "importer": "Media Importer",
        "id": 789
      },
      {
        "importer": "Item Importer",
        "id": 790
      }
    ],
    "number_of_itemsets": 86,
    "number_of_items": 12,
    "number_of_media": 12
  }
]
```

### Incremental Updates

The JSON reporter updates the output file after each channel is migrated. This ensures that if the migration process is interrupted, the information collected up to that point is preserved in the output file.

## Implementation Details

The JSON reporter is implemented in the `src/json_reporter.py` module. It provides the following functionality:

- Creating or updating a JSON file with migration results
- Counting XML tags in the exported WordPress data to determine the number of itemsets, items, and media
- Adding channel reports to the JSON file incrementally

## Testing

You can test the JSON reporter functionality using the `test_json_reporter.py` script:

```bash
python test_json_reporter.py --output-file <output_file> --xml-file <xml_file>
```

This script creates a sample channel report and adds it to the specified output file.
