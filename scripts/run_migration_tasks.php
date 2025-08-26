#!/usr/bin/env php
<?php
/**
 * Run Migration Tasks Script
 *
 * This script reads a JSON file with migration tasks information,
 * executes the bulk import tasks, and updates the JSON with job IDs
 * and additional information.
 *
 * Usage:
 *   php run_migration_tasks.php --input-file <input_file> --output-file <output_file> [--mark-completed] [--omeka-path <path>]
 *
 * Arguments:
 *   --input-file     Path to the input JSON file with migration tasks information
 *   --output-file    Path to the output JSON file to write the updated information
 *   --mark-completed Mark the original tasks as completed (optional)
 *   --omeka-path     Path to the Omeka S installation (default: /var/www/html)
 *
 * Author: [Your Name]
 * Date: 26-08-2025
 */

// Define constants
define('SCRIPT_VERSION', '1.0.0');

// Parse command line arguments
$options = getopt('', ['input-file:', 'output-file:', 'mark-completed', 'omeka-path::']);

// Validate required arguments
if (!isset($options['input-file']) || !isset($options['output-file'])) {
    echo "Error: Missing required arguments.\n";
    echo "Usage: php run_migration_tasks.php --input-file <input_file> --output-file <output_file> [--mark-completed] [--omeka-path <path>]\n";
    exit(1);
}

$inputFile = $options['input-file'];
$outputFile = $options['output-file'];
$markCompleted = isset($options['mark-completed']);
$omekaPath = isset($options['omeka-path']) ? $options['omeka-path'] : '/var/www/html';

// Validate input file
if (!file_exists($inputFile)) {
    echo "Error: Input file not found: $inputFile\n";
    exit(1);
}

// Read input JSON file
echo "Reading input file: $inputFile\n";
$jsonContent = file_get_contents($inputFile);
$migrationData = json_decode($jsonContent, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    echo "Error: Invalid JSON in input file: " . json_last_error_msg() . "\n";
    exit(1);
}

// Initialize Omeka S application
echo "Initializing Omeka S application...\n";
require_once "$omekaPath/bootstrap.php";

// Get the application
$application = Omeka\Mvc\Application::init(require "$omekaPath/application/config/application.config.php");
$serviceLocator = $application->getServiceManager();
$entityManager = $serviceLocator->get('Omeka\EntityManager');
$api = $serviceLocator->get('Omeka\ApiManager');

// Process each channel in the migration data
$totalChannels = count($migrationData);
echo "Processing $totalChannels channels...\n";

foreach ($migrationData as $index => &$channel) {
    $channelName = $channel['name'];
    $siteId = $channel['site_id'];
    echo "Processing channel ($index+1/$totalChannels): $channelName (Site ID: $siteId)\n";
    
    // Process each task in the channel
    foreach ($channel['tasks_created'] as &$task) {
        $taskId = $task['id'];
        $importerName = $task['importer'];
        echo "  - Processing task: $importerName (ID: $taskId)\n";
        
        // Execute the task.php script
        $jobId = executeTask($taskId, $omekaPath);
        
        // Add job ID to the task
        $task['job_id'] = $jobId;
        
        // Mark the task as completed if requested
        if ($markCompleted && $jobId) {
            markTaskCompleted($taskId, $entityManager);
        }
    }
    
    // Get item sets and items count for the site
    $counts = getItemCounts($siteId, $api);
    
    // Add counts to the channel data
    $channel['omeka_itemsets_count'] = $counts['itemSetsCount'];
    $channel['omeka_items_count'] = $counts['itemsCount'];
}

// Write updated JSON to output file
echo "Writing output file: $outputFile\n";
file_put_contents($outputFile, json_encode($migrationData, JSON_PRETTY_PRINT));

echo "Migration tasks processing completed successfully.\n";
exit(0);

/**
 * Execute a bulk import task using the task.php script.
 *
 * @param int $taskId The ID of the bulk import task
 * @param string $omekaPath The path to the Omeka S installation
 * @return string|null The job ID if successful, null otherwise
 */
function executeTask($taskId, $omekaPath) {
    $taskScript = "$omekaPath/modules/EasyAdmin/data/scripts/task.php";
    
    // Check if the task script exists
    if (!file_exists($taskScript)) {
        echo "    Error: Task script not found: $taskScript\n";
        return null;
    }
    
    // Build the command
    $command = sprintf(
        'php %s --task %s --user-id %d --args %s',
        escapeshellarg($taskScript),
        escapeshellarg('BulkImport\Job\Import'),
        1, // User ID (admin)
        escapeshellarg(json_encode(['bulk_import_id' => (int)$taskId]))
    );
    
    echo "    Executing command: $command\n";
    
    // Execute the command
    $output = [];
    $returnCode = 0;
    exec($command, $output, $returnCode);
    
    // Check if the command was successful
    if ($returnCode !== 0) {
        echo "    Error: Command failed with return code $returnCode\n";
        echo "    Output: " . implode("\n", $output) . "\n";
        return null;
    }
    
    // Extract job ID from the output
    $jobId = null;
    foreach ($output as $line) {
        if (preg_match('/Task .+ is starting \(job: #(\d+)\)/', $line, $matches)) {
            $jobId = $matches[1];
            echo "    Job ID: $jobId\n";
            break;
        }
    }
    
    if (!$jobId) {
        echo "    Warning: Could not extract job ID from output\n";
        echo "    Output: " . implode("\n", $output) . "\n";
    }
    
    return $jobId;
}

/**
 * Mark a bulk import task as completed.
 *
 * @param int $taskId The ID of the bulk import task
 * @param EntityManager $entityManager The Doctrine entity manager
 * @return bool True if successful, false otherwise
 */
function markTaskCompleted($taskId, $entityManager) {
    try {
        // Get the bulk import entity
        $bulkImport = $entityManager->find('BulkImport\Entity\Import', $taskId);
        
        if (!$bulkImport) {
            echo "    Error: Bulk import task not found: $taskId\n";
            return false;
        }
        
        // Update the status to completed
        $bulkImport->setStatus('completed');
        $entityManager->flush();
        
        echo "    Task marked as completed\n";
        return true;
    } catch (Exception $e) {
        echo "    Error marking task as completed: " . $e->getMessage() . "\n";
        return false;
    }
}

/**
 * Get the count of item sets and items for a site.
 *
 * @param int $siteId The ID of the site
 * @param ApiManager $api The Omeka API manager
 * @return array An array with itemSetsCount and itemsCount
 */
function getItemCounts($siteId, $api) {
    $counts = [
        'itemSetsCount' => 0,
        'itemsCount' => 0
    ];
    
    try {
        // Get the site
        $site = $api->read('sites', $siteId)->getContent();
        
        if (!$site) {
            echo "    Error: Site not found: $siteId\n";
            return $counts;
        }
        
        // Get item sets count for the site
        $itemSetsResponse = $api->search('item_sets', ['site_id' => $siteId]);
        $counts['itemSetsCount'] = $itemSetsResponse->getTotalResults();
        
        // Get items count for the site
        $itemsResponse = $api->search('items', ['site_id' => $siteId]);
        $counts['itemsCount'] = $itemsResponse->getTotalResults();
        
        echo "    Site counts - Item Sets: " . $counts['itemSetsCount'] . ", Items: " . $counts['itemsCount'] . "\n";
    } catch (Exception $e) {
        echo "    Error getting item counts: " . $e->getMessage() . "\n";
    }
    
    return $counts;
}
