# WordPress to Omeka S Migration Tool

This tool automates the migration of WordPress sites to Omeka S. It reads a CSV file with channel information and performs the migration process.

## Features

- Read channel information from a CSV file
- Create sites in Omeka S
- Create users in Omeka S
- Add users to sites
- Export WordPress data
- Create bulk importers in Omeka S
- Create bulk import jobs in Omeka S
- Configure migration using JSON configuration files

## Project Structure

```
src/
├── Omeka/                  # Omeka S related modules
│   ├── OmekaAdapter.py     # Module to interact with Omeka S API
│   └── UserAdapter.py      # Module to handle user operations (to be implemented)
├── WordPress/              # WordPress related modules
│   └── WordPressExporter.py # Module to export WordPress data
├── CAS_login.py            # Module for CAS authentication
├── csv_reader.py           # Module to read channel information from CSV
├── logger.py               # Module for logging
├── main.py                 # Main entry point
├── migration_manager.py    # Module to manage the migration process
├── Migration_process.py    # Original migration process (for reference)
└── test_migration.py       # Module to test the migration process
```

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
python quick_start.py --omeka-url <omeka_url> --key-identity <key_identity> --key-credential <key_credential> --wp-username <username> --wp-password <password> --channel-url <url>
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
- `--as-task`: Save as task (y) or execute immediately (n). Default: n
- `--execute-tasks`: JSON string with bulk_import_ids to execute: `'{"bulk_import_id":[1,2,3]}'`

This script will:
1. Check if the required packages are installed (and install them if needed)
2. Create the necessary directories
3. Run a test migration for a single channel

### Run All

You can also run all the scripts in the correct order:

```
python run_all.py --omeka-url <omeka_url> --key-identity <key_identity> --key-credential <key_credential> --wp-username <username> --wp-password <password>
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
- `--as-task`: Save as task (y) or execute immediately (n). Default: n
- `--execute-tasks`: JSON string with bulk_import_ids to execute: `'{"bulk_import_id":[1,2,3]}'`

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
- `--as-task`: Save as task (y) or execute immediately (n). Default: n
- `--execute-tasks`: JSON string with bulk_import_ids to execute: `'{"bulk_import_id":[1,2,3]}'`

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
- `--as-task`: Save as task (y) or execute immediately (n). Default: n
- `--execute-tasks`: JSON string with bulk_import_ids to execute: `'{"bulk_import_id":[1,2,3]}'`

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

Example:
```
name,url,slug,editor
Channel 1,https://example.com/channel1,channel1,user1
Channel 2,https://example.com/channel2,channel2,user2
```

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

## New Parameters

### --as-task Parameter

The `--as-task` parameter controls how bulk import jobs are handled:

- **`--as-task n`** (default): Bulk import jobs are executed immediately by Omeka S
  - The `as_task` parameter in the configuration is set to "0"
  - Omeka S starts the migration process immediately when the bulk import job is created
  - Suitable for smaller migrations or when you want immediate processing

- **`--as-task y`**: Bulk import jobs are saved as tasks for later execution
  - The `as_task` parameter in the configuration is set to "1"
  - Omeka S saves the bulk import as a task that can be executed later using command line tools
  - Suitable for larger migrations or when you want to control when the processing happens

Example usage:
```bash
# Execute immediately (default)
python main.py --csv channels.csv --omeka-url https://example.com/api --key-identity key --key-credential cred --wp-username user --wp-password pass --as-task n

# Save as tasks for later execution
python main.py --csv channels.csv --omeka-url https://example.com/api --key-identity key --key-credential cred --wp-username user --wp-password pass --as-task y
```

### --execute-tasks Parameter

The `--execute-tasks` parameter allows you to execute previously created bulk import tasks:

- **Format**: JSON string with the format `'{"bulk_import_id":[1,2,3]}'`
- **Behavior**: When this parameter is provided, the program skips the normal migration process (creating sites, users, exporters, etc.) and only executes the specified tasks
- **Execution**: Uses the PHP command line tool to execute each task: 
  ```bash
  php '/var/www/html/modules/EasyAdmin/data/scripts/task.php' --task 'BulkImport\Job\Import' --user-id 1 --args '{"bulk_import_id": TASK_ID}'
  ```

Example usage:
```bash
# Execute specific bulk import tasks
python main.py --csv channels.csv --omeka-url https://example.com/api --key-identity key --key-credential cred --wp-username user --wp-password pass --execute-tasks '{"bulk_import_id":[505,506,507]}'
```

### Workflow Examples

#### Two-Step Migration Process

1. **Step 1**: Create migration structure and save as tasks
   ```bash
   python main.py --csv channels.csv --omeka-url https://example.com/api --key-identity key --key-credential cred --wp-username user --wp-password pass --as-task y
   ```
   This creates sites, users, exports data, and creates bulk import jobs saved as tasks.

2. **Step 2**: Execute the tasks when ready
   ```bash
   python main.py --csv channels.csv --omeka-url https://example.com/api --key-identity key --key-credential cred --wp-username user --wp-password pass --execute-tasks '{"bulk_import_id":[1,2,3,4,5]}'
   ```
   This executes the previously created tasks.

#### Single-Step Migration Process

```bash
python main.py --csv channels.csv --omeka-url https://example.com/api --key-identity key --key-credential cred --wp-username user --wp-password pass --as-task n
```
This creates the complete migration structure and executes the bulk imports immediately.

## Implemented Features

The following features have been implemented:
- Migration of WordPress channels to Omeka S sites
- Creation of users and assignment to sites
- Export of WordPress data to XML
- Creation of bulk importers in Omeka S
- Creation of bulk import jobs in Omeka S
- Task-based execution control with `--as-task` parameter
- Selective task execution with `--execute-tasks` parameter

## Running task
```sudo -u www-data php '/path/to/omeka/modules/EasyAdmin/data/scripts/task.php' --task 'BulkImport\Job\Import' --user-id 1 --server-url 'https://example.org' --base-path '/omeka-s' --args '{"bulk_import_id": 1}'```
