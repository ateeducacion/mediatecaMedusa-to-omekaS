# WordPress to Omeka S Migration Tool

This tool automates the migration of WordPress sites to Omeka S. It reads a CSV file with channel information and performs the migration process.

## Features

- Read channel information from a CSV file
  - Support for comment lines starting with '#'
- Create sites in Omeka S
- Create users in Omeka S
- Add users to sites
- Export WordPress data
  - Error handling to continue processing when download fails
- Create bulk importers in Omeka S
- Create bulk import jobs in Omeka S
- Configure migration using JSON configuration files
- Detailed JSON reports with status information for each channel

## Project Structure

- src/ (core Python modules)
  - Omeka/ (Omeka S related modules)
    - OmekaAdapter.py     # Module to interact with Omeka S API
    - UserAdapter.py      # Module to handle user operations
  - WordPress/              # WordPress related modules
    - WordPressExporter.py # Module to export WordPress data
  - common/
    - CAS_login.py            # Module for CAS authentication
  - csv_reader.py           # Module to read channel information from CSV
  - logger.py               # Module for logging
  
  - migration_manager.py    # Module to manage the migration process
  - Migration_process.py    # Original migration process (for reference)
  - test_migration.py       # Module to test the migration process
- setup_project.py            # Project bootstrap tooling
- exports/                  #Downloaded XML files from channels
- README_download_channels.md  # Documentation
- README_json_reporter.md      # Documentation
- README.md                    # This file
- main.py                      # Present at root (entry point for some workflows)
- quick_start.py               # Quick start helper
- run_all.py                   # Run all scripts in sequence
- run_migration.py             # Migration runner
- run_test_migration.py        # Test migration runner
- run_tests.py                 # Test runner
- run_coverage.py              # Coverage runner
- docs/                        # Documentation sources
- tests/                       # Unit tests
- migration_config.json        # Migration configuration

## Requirements

- Python 3.6 or higher
- Required Python packages:
  - requests
  - typing
  - coverage (for running tests with coverage)
  - pdoc (for generating documentation)
- Environment variable $OMEKA_PATH must be set to Omeka-S root path. '/var/www/html' is taken by default

You can install the required packages with:

```
python install_requirements.py
```

You can also upgrade packages to the latest version:

```
python install_requirements.py --upgrade
```

Or install packages in user space:

```
python install_requirements.py --user
```

## Usage

### Quick Start

The easiest way to get started is to use the quick start script:

```
python quick_start.py --omeka-url <omeka_url> --key-identity <key_identity> --key-credential <key_credential> --wp-username <username> --wp-password <password> --channel-url <url> --output-file <output_file>
```

Arguments:
- `--omeka-url`: Omeka S API URL
- `--key-identity`: Omeka S API key identity
- `--key-credential`: Omeka S API key credential
- `--wp-username`: WordPress username
- `--wp-password`: WordPress password
- `--channel-url`: URL of the channel
- `--config`: Path to migration configuration file (default: migration_config.json)
- `--log-level`: Set the logging level (default: INFO)
- `--output-file`: Path to the output JSON file with migration results

### Run All

You can also run all the scripts in the correct order:

```
python run_all.py --omeka-url <omeka_url> --key-identity <key_identity> --key-credential <key_credential> --wp-username <username> --wp-password <password> --output-file <output_file>
```

Arguments:
- `--omeka-url`: Omeka S API URL
- `--key-identity`: Omeka S API key identity
- `--key-credential`: Omeka S API key credential
- `--wp-username`: WordPress username
- `--wp-password`: WordPress password
- `--csv`: Path to CSV file with channel information (default: example_channels.csv)
- `--config`: Path to migration configuration file (default: migration_config.json)
- `--log-level`: Set the logging level (default: INFO)
- `--skip-tests`: Skip running tests
- `--skip-coverage`: Skip running coverage
- `--skip-docs`: Skip generating documentation
- `--output-file`: Path to the output JSON file with migration results

This script will:
1. Check if the required packages are installed (and install them if needed)
2. Create the necessary directories
3. Run the tests
4. Run the tests with coverage
5. Generate documentation
6. Run the migration

### Main Script

For migrating multiple channels from a CSV file:

```
python main.py --csv <csv_file> --omeka-url <omeka_url> --key-identity <key_identity> --key-credential <key_credential> --wp-username <username> --wp-password <password> --config <config_file>
```

Arguments:
- `--csv`: Path to CSV file with channel information
- `--omeka-url`: Omeka S API URL
- `--key-identity`: Omeka S API key identity
- `--key-credential`: Omeka S API key credential
- `--wp-username`: WordPress username
- `--wp-password`: WordPress password
- `--config`: Path to migration configuration file
- `--log-level`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--output-file`: Path to the output JSON file with migration results

You can also use the run_migration.py script for a simpler interface:

```
python run_migration.py --omeka-url <omeka_url> --key-identity <key_identity> --key-credential <key_credential> --wp-username <username> --wp-password <password> --config <config_file>
```

### Test Script

For testing the migration process with a single channel:

```
python test_migration.py --omeka-url <omeka_url> --key-identity <key_identity> --key-credential <key_credential> --wp-username <username> --wp-password <password> --channel-name <name> --channel-url <url> --channel-editor <editor>
```

Arguments:
- `--omeka-url`: Omeka S API URL
- `--key-identity`: Omeka S API key identity
- `--key-credential`: Omeka S API key credential
- `--wp-username`: WordPress username
- `--wp-password`: WordPress password
- `--channel-name`: Name of the channel
- `--channel-url`: URL of the channel
- `--channel-slug`: Slug of the channel (optional, will be generated from name if not provided)
- `--channel-editor`: Username of the editor
- `--config`: Path to migration configuration file
- `--log-level`: Set the logging level (default: INFO)
- `--output-file`: Path to the output JSON file with migration results

You can also use the run_test_migration.py script for a simpler interface:

```
python run_test_migration.py --omeka-url <omeka_url> --key-identity <key_identity> --key-credential <key_credential> --wp-username <username> --wp-password <password> --channel-url <url>
```

### Other Scripts

- `setup.py`: Creates the necessary directories and files for the project
- `check_requirements.py`: Checks if the required packages are installed
- `create_init_files.py`: Creates empty __init__.py files in each directory to make them proper Python packages
- `run_tests.py`: Runs all the tests for the project
- `clean.py`: Cleans up the project by removing generated files

You can clean up the project with:

```
python clean.py
```

You can also remove all generated files (including logs and exports):

```
python clean.py --all
```

### Tests

The project includes unit tests to ensure the code works as expected. To run the tests:

```
python run_tests.py
```

You can also run the tests with verbose output:

```
python run_tests.py --verbose
```

The tests are located in the `tests` directory and follow the naming convention `test_*.py`.

### Coverage

You can run the tests with coverage to see how much of the code is covered by tests:

```
python run_coverage.py
```

You can also generate an HTML coverage report:

```
python run_coverage.py --html
```

The HTML report will be generated in the `coverage` directory.

### Documentation

You can generate documentation for the project using pdoc:

```
python generate_docs.py
```

You can also specify a custom output directory:

```
python generate_docs.py --output-dir custom_docs
```

The documentation will be generated in the specified directory (default: `docs`).

## CSV File Format

The CSV file should have the following columns:
- `name`: Name of the channel
- `url`: Web address of the channel
- `slug`: Slug of the channel
- `editor`: Username of the editor

Lines starting with '#' are treated as comments and ignored during processing. This allows you to add explanatory notes or temporarily disable certain channels without removing them from the file.

Example:
```
name,url,slug,editor
# This is a comment line explaining the CSV format
# name: Name of the channel
# url: Web address of the channel
# slug: Slug of the channel (optional, will be generated from name if empty)
# editor: Username of the editor
Channel 1,https://example.com/channel1,channel1,user1
# This channel is for testing purposes
Channel 2,https://example.com/channel2,channel2,user2
# The following channel is the main one
Channel 3,https://example.com/channel3,channel3,user3
```

An example CSV file with comments is provided in the project root directory: `example_channels_with_comments.csv`.

## Configuration File

The migration process can be configured using a JSON file. The file should have the following structure:

```json
{
  "importers": [
    {
      "@type": "o-bulk:Importer",
      "o:label": "Importer Label",
      "o-bulk:reader": "BulkImport\\Reader\\XmlReader",
      "o-bulk:mapper": {
        "@type": "o-bulk:Mapping",
        "o:label": "mapper_label"
      },
      "o-bulk:processor": "BulkImport\\Processor\\ProcessorType",
      "o:config": {
        "importer": {
          "as_task": "1",
          "notify_end": "0"
        },
        "reader": {
          "url": "",
          "list_files": [],
          "xsl_sheet_pre": "module:xsl/transformation.xsl",
          "xsl_sheet": "",
          "xsl_params": []
        },
        "processor": {
          "processing": "continue_on_error",
          "skip_missing_files": false,
          "entries_to_skip": 0,
          "entries_max": 0,
          "info_diffs": false,
          "action": "create",
          "action_unidentified": "create",
          "identifier_name": null,
          "value_datatype_literal": false,
          "allow_duplicate_identifiers": false,
          "action_identifier_update": "append",
          "action_media_update": "append",
          "action_item_set_update": "append",
          "o:resource_template": null,
          "o:resource_class": null,
          "o:owner": "current",
          "o:is_public": false,
          "o:thumbnail": null
        }
      }
    }
  ]
}
```

The configuration file has one main section:

1. `importers`: Configuration for each bulk importer
   - `@type`: The type of the importer (usually "o-bulk:Importer")
   - `o:label`: The label of the importer
   - `o-bulk:reader`: The reader class to use
   - `o-bulk:mapper`: The mapper to use
   - `o-bulk:processor`: The processor class to use
   - `o:config`: Configuration for the importer, reader, and processor

A sample configuration file is provided in the project root directory: `migration_config.json`.

## JSON Report Format

When using the `--output-file` parameter, the migration process generates a JSON report with detailed information about each channel. The report includes:

- `name`: Name of the channel
- `url`: Web address of the channel
- `slug`: Slug of the channel
- `editor`: Username of the editor
- `site_id`: ID of the created site in Omeka S
- `user_id`: ID of the created user in Omeka S
- `user_login`: Username of the created user
- `tasks_created`: List of created import jobs
  - `importer`: Label of the importer
  - `id`: ID of the import job
- `number_of_itemsets`: Number of item sets in the exported XML
- `number_of_items`: Number of items in the exported XML
- `number_of_media`: Number of media in the exported XML
- `status`: Status of the migration ('success' or 'error')
- `error_message`: Error message if the migration failed (null if successful)

The status field indicates whether the migration was successful or if there was an error. If there was an error, the error_message field provides more information about what went wrong. This allows you to easily identify channels that failed to migrate and take appropriate action.

Example:
```json
[
  {
    "name": "Channel 1",
    "url": "https://example.com/channel1",
    "slug": "channel1",
    "editor": "user1",
    "site_id": 1,
    "user_id": 1,
    "user_login": "user1",
    "tasks_created": [
      {
        "importer": "WordPress XML Importer",
        "id": 1
      }
    ],
    "number_of_itemsets": 5,
    "number_of_items": 10,
    "number_of_media": 20,
    "status": "success",
    "error_message": null
  },
  {
    "name": "Channel 2",
    "url": "https://example.com/channel2",
    "slug": "channel2",
    "editor": "user2",
    "site_id": 2,
    "user_id": 2,
    "user_login": "user2",
    "tasks_created": [],
    "number_of_itemsets": 0,
    "number_of_items": 0,
    "number_of_media": 0,
    "status": "error",
    "error_message": "Failed to export data from WordPress"
  }
]
```

## Bulk Import Process

The migration process follows these steps:

1. **Initialization**: When the MigrationManager is created with a configuration file, it immediately creates all the bulk importers defined in the configuration. This ensures that importers are created only once, not once per site.

2. **Channel Migration**: For each channel in the CSV file:
   - Create a site in Omeka S
   - Create a user in Omeka S
   - Add the user to the site
   - Export WordPress data to XML
   - Create bulk import jobs for this channel using all available importers

For each channel and each importer, a bulk import job is created with the following configuration:
- The XML file exported for the channel
- The site name for the comment
- The user ID for the owner of the imported resources

This approach ensures that:
- Importers are created only once, not once per site
- Import jobs are created for each channel during its migration
- Each import job is properly configured with the correct XML file, site name, and owner ID
- If there's an error exporting data from WordPress, the migration process continues with the next channel and records the error in the JSON report
