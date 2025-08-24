# Channel Download Script

This script downloads export files for WordPress channels listed in `exports/mediatecas.csv` using the WordPressExporter module.

## Features

- Downloads WordPress export files for all channels in the CSV file
- Shows detailed progress information during the download process
- Allows starting from a specific channel number
- Logs all operations to both console and a log file
- Provides detailed error reporting

## Requirements

- Python 3.6 or higher
- Access credentials for the WordPress sites

## Installation

No additional installation is required. The script uses modules that are already part of the project.

## Usage

```bash
python download_channels.py --username USERNAME --password PASSWORD [--start CHANNEL_NUMBER]
```

### Parameters

- `--username`: Username for WordPress authentication (required)
- `--password`: Password for WordPress authentication (required)
- `--start`: Channel number to start from (optional)
- `--stop`: Channel number to stop at (optional)
- `--output-dir`: Directory to save exported files (default: 'exports/channels')
- `--csv-path`: Path to the CSV file with channel information (default: 'exports/mediatecas.csv')

### Examples

1. Download all channels:

```bash
python download_channels.py --username user@example.com --password mypassword
```

2. Start downloading from channel number 50:

```bash
python download_channels.py --username user@example.com --password mypassword --start 50
```

3. Download channels from number 50 to 100:

```bash
python download_channels.py --username user@example.com --password mypassword --start 50 --stop 100
```

4. Download channels up to number 100:

```bash
python download_channels.py --username user@example.com --password mypassword --stop 100
```

5. Specify a different output directory:

```bash
python download_channels.py --username user@example.com --password mypassword --output-dir my_exports
```

## Output

The script will:

1. Create the output directory if it doesn't exist
2. Download each channel's export as an XML file
3. Name each file based on the channel name
4. Show progress information including:
   - Current channel being processed (e.g., 10/100)
   - Channel name and number
   - URL being accessed
   - Download completion status
   - File size
   - Time taken for each download

## Logging

All operations are logged to:
- Console (stdout)
- A log file named `download_channels.log`

The log includes detailed information about each step of the process, including any errors that occur.

## Error Handling

If an error occurs during the download of a specific channel, the script will:
1. Log the error
2. Display an error message
3. Continue with the next channel

This ensures that a single failed download doesn't stop the entire process.
