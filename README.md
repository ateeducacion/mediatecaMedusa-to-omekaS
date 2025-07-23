# WordPress to Omeka S Migration Tool

This tool automates the migration of WordPress sites to Omeka S. It reads a CSV file with channel information and performs the migration process.

## Features

- Read channel information from a CSV file
- Create sites in Omeka S
- Create users in Omeka S
- Add users to sites
- Export WordPress data
- Prepare for future job creation (to be implemented in future iterations)

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
python quick_start.py --omeka-url <omeka_url> --wp-username <username> --wp-password <password> --channel-url <url>
```

Arguments:
- `--omeka-url`: Omeka S API URL
- `--wp-username`: WordPress username
- `--wp-password`: WordPress password
- `--channel-url`: URL of the channel

This script will:
1. Check if the required packages are installed (and install them if needed)
2. Create the necessary directories
3. Run a test migration for a single channel

### Run All

You can also run all the scripts in the correct order:

```
python run_all.py --omeka-url <omeka_url> --wp-username <username> --wp-password <password>
```

Arguments:
- `--omeka-url`: Omeka S API URL
- `--wp-username`: WordPress username
- `--wp-password`: WordPress password
- `--csv`: Path to CSV file with channel information (default: example_channels.csv)
- `--log-level`: Set the logging level (default: INFO)
- `--skip-tests`: Skip running tests
- `--skip-coverage`: Skip running coverage
- `--skip-docs`: Skip generating documentation

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
python main.py --csv <csv_file> --omeka-url <omeka_url> --wp-username <username> --wp-password <password>
```

Arguments:
- `--csv`: Path to CSV file with channel information
- `--omeka-url`: Omeka S API URL
- `--wp-username`: WordPress username
- `--wp-password`: WordPress password
- `--log-level`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

You can also use the run_migration.py script for a simpler interface:

```
python run_migration.py --omeka-url <omeka_url> --wp-username <username> --wp-password <password>
```

### Test Script

For testing the migration process with a single channel:

```
python test_migration.py --omeka-url <omeka_url> --wp-username <username> --wp-password <password> --channel-name <name> --channel-url <url> --channel-editor <editor>
```

Arguments:
- `--omeka-url`: Omeka S API URL
- `--wp-username`: WordPress username
- `--wp-password`: WordPress password
- `--channel-name`: Name of the channel
- `--channel-url`: URL of the channel
- `--channel-slug`: Slug of the channel (optional, will be generated from name if not provided)
- `--channel-editor`: Username of the editor

You can also use the run_test_migration.py script for a simpler interface:

```
python run_test_migration.py --omeka-url <omeka_url> --wp-username <username> --wp-password <password> --channel-url <url>
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

## Future Iterations

The following features will be implemented in future iterations:
- Migration of item sets
- Migration of items
- Migration of media
- Execution of jobs
