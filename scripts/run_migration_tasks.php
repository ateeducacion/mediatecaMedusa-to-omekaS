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
 *   php run_migration_tasks.php --input-file <input_file> --output-file <output_file> [--delete-tasks] [--omeka-path <path>]
 *
 * Arguments:
 *   --input-file     Path to the input JSON file with migration tasks information
 *   --output-file    Path to the output JSON file to write the updated information
 *   --delete-tasks   Delete the original tasks after execution (optional)
 *   --omeka-path     Path to the Omeka S installation (default: /var/www/html)
 *
 * Author: [Your Name]
 * Date: 26-08-2025
 */

// Define constants
define('SCRIPT_VERSION', '1.0.0');

// Parse command line arguments
$options = getopt('', ['input-file:', 'output-file:', 'delete-tasks', 'omeka-path:']);

// Validate required arguments
if (!isset($options['input-file']) || !isset($options['output-file'])) {
    echo "Error: Missing required arguments.\n";
    echo "Usage: php run_migration_tasks.php --input-file <input_file> --output-file <output_file> [--delete-tasks] [--omeka-path <path>]\n";
    exit(1);
}

$inputFile = $options['input-file'];
$outputFile = $options['output-file'];
$deleteTasks = isset($options['delete-tasks']);
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

// Get the authentication service and set the admin user (ID 1) for API operations
$auth = $serviceLocator->get('Omeka\AuthenticationService');
$userAdapter = $serviceLocator->get('Omeka\ApiAdapterManager')->get('users');
$adminUser = $entityManager->find('Omeka\Entity\User', 1); // Admin user (ID 1)
if ($adminUser) {
    $auth->getStorage()->write($adminUser);
    echo "Using admin user for API operations\n";
} else {
    echo "Warning: Admin user not found. Some operations may fail due to permission issues.\n";
}

// Process each channel in the migration data
$totalChannels = count($migrationData);
echo "Processing $totalChannels channels...\n";

// Initialize or read existing output data
$outputData = [];
if (file_exists($outputFile)) {
    $existingContent = file_get_contents($outputFile);
    $existingData = json_decode($existingContent, true);
    if (json_last_error() === JSON_ERROR_NONE && is_array($existingData)) {
        $outputData = $existingData;
    }
}

foreach ($migrationData as $index => &$channel) {
    $channelName = $channel['name'];
    $siteId = $channel['site_id'];
    echo "Processing channel (" . ($index+1) . "/$totalChannels): $channelName (Site ID: $siteId)\n";
    
    // Process each task in the channel
    foreach ($channel['tasks_created'] as &$task) {
        $taskId = $task['id'];
        $importerName = $task['importer'];
        echo "  - Processing task: $importerName (ID: $taskId)\n";
        
        // Execute the task.php script
        $jobId = executeTask($taskId, $omekaPath);
        
        // Add job ID to the task
        $task['job_id'] = $jobId;
        
        if ($jobId) {
            // Get the new bulk import task created for this job
            $newTaskId = getNewBulkImportTaskId($jobId, $entityManager);
            if ($newTaskId) {
                $task['new_task_id'] = $newTaskId;
                echo "    New bulk import task ID: $newTaskId\n";
            }
            
            // Delete the original task if requested
            if ($deleteTasks) {
                deleteTask($taskId, $entityManager);
            }
        }
    }
    

    // Add item sets with matching dcterms:subject to the site
    addItemSetsToSite($siteId, $api, $entityManager);

    // Add site_id to user's default_item_sites
    if (isset($channel['user_id'])) {
        $userId = $channel['user_id'];
        addSiteToUserDefaultItemSites($userId, $siteId, $api, $entityManager);
    }

    // Get item sets and items count for the site
    $counts = getItemCounts($siteId, $api);

    // Add counts to the channel data
    $channel['omeka_itemsets_count'] = $counts['itemSetsCount'];
    $channel['omeka_items_count'] = $counts['itemsCount'];
    $channel['omeka_media_count'] = $counts['mediaCount'];
    
    // Write this channel's data to the output file immediately
    $outputData[$index] = $channel;
    echo "  Writing channel data to output file: $outputFile\n";
    file_put_contents($outputFile, json_encode(array_values($outputData), JSON_PRETTY_PRINT));
    echo "  Channel (" . ($index+1) . "/$totalChannels) data written successfully.\n";
}

// Final confirmation
echo "All channel data has been written to output file: $outputFile\n";

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
 * Get the new bulk import task ID created for a job.
 *
 * @param string $jobId The ID of the job
 * @param EntityManager $entityManager The Doctrine entity manager
 * @return int|null The new bulk import task ID if found, null otherwise
 */
function getNewBulkImportTaskId($jobId, $entityManager) {
    try {
        // Get the job entity
        $job = $entityManager->find('Omeka\Entity\Job', $jobId);
        
        if (!$job) {
            echo "    Error: Job not found: $jobId\n";
            return null;
        }
        
        // Query for bulk import tasks associated with this job
        $qb = $entityManager->createQueryBuilder();
        $qb->select('bi')
           ->from('BulkImport\Entity\Import', 'bi')
           ->where('bi.job = :job')
           ->setParameter('job', $job);
        
        $query = $qb->getQuery();
        $result = $query->getResult();
        
        if (empty($result)) {
            echo "    Warning: No new bulk import task found for job: $jobId\n";
            return null;
        }
        
        // Return the ID of the first bulk import task found
        $newTask = reset($result);
        return $newTask->getId();
    } catch (Exception $e) {
        echo "    Error getting new bulk import task ID: " . $e->getMessage() . "\n";
        return null;
    }
}

/**
 * Delete a bulk import task.
 *
 * @param int $taskId The ID of the bulk import task
 * @param EntityManager $entityManager The Doctrine entity manager
 * @return bool True if successful, false otherwise
 */
function deleteTask($taskId, $entityManager) {
    try {
        // Get the bulk import entity
        $bulkImport = $entityManager->find('BulkImport\Entity\Import', $taskId);
        
        if (!$bulkImport) {
            echo "    Error: Bulk import task not found: $taskId\n";
            return false;
        }
        
        // Remove the entity
        $entityManager->remove($bulkImport);
        $entityManager->flush();
        
        echo "    Task deleted\n";
        return true;
    } catch (Exception $e) {
        echo "    Error deleting task: " . $e->getMessage() . "\n";
        return false;
    }
}

/**
 * Add item sets with matching dcterms:subject to the site and clear the subject field.
 * Uses the API with admin user permissions.
 *
 * @param int $siteId The ID of the site
 * @param ApiManager $api The Omeka API manager
 * @param EntityManager $entityManager The Doctrine entity manager
 * @return int Number of item sets added to the site
 */
function addItemSetsToSite($siteId, $api, $entityManager) {
    try {
        $entityManager->clear(); // to avoid cache issues
        echo "    Adding item sets to site (ID: $siteId) using API with admin user...\n";
        
        // Get the site
        $site = $api->read('sites', $siteId)->getContent();
        if (!$site) {
            echo "    Error: Site not found: $siteId\n";
            return 0;
        }
        
        // Get current site item sets
        $siteItemSets = $site->siteItemSets();
        $currentItemSetIds = [];
        foreach ($siteItemSets as $siteItemSet) {
            $currentItemSetIds[] = $siteItemSet->itemSet()->id();
        }
        
        
        // Find item sets with dcterms:subject matching the site ID
        $query = [
            'property' => [
                [
                    'property' => 'dcterms:subject',
                    'type' => 'eq',
                    'text' => (string)$siteId
                ]
            ]
        ];
        
        $response = $api->search('item_sets', $query);
        $itemSets = $response->getContent();
        
        if (empty($itemSets)) {
            echo "    No item sets found with dcterms:subject matching site ID: $siteId\n";
            return 0;
        }
        
        // Add item sets to the site
        $addedCount = 0;
        $updatedSiteData = [
            'o:site_item_set' => []
        ];
        
        // Add existing site item sets
        $position = 1;
        foreach ($currentItemSetIds as $itemSetId) {
            $updatedSiteData['o:site_item_set'][] = [
                'o:item_set' => ['o:id' => $itemSetId]
            ];
        }
        
        // Add new item sets
        foreach ($itemSets as $itemSet) {
            
            $itemSetId = $itemSet->id();
            
            // Skip if already in the site
            if (in_array($itemSetId, $currentItemSetIds)) {
                continue;
            }
            
            // Prepare item set data for update
            $itemSetData = cleanItemSetForUpdate($itemSet);
            
            // Only remove the dcterms:subject field, not all fields
            if (isset($itemSetData['dcterms:subject'])) {
                $itemSetData['dcterms:subject']= [];
                $itemSetData=json_decode(json_encode($itemSetData),true);
                // Update only the dcterms:subject field
                $api->update('item_sets', $itemSetId, $itemSetData, [], ['isPartial' => true]);
            }
            // Add to site
            $updatedSiteData['o:site_item_set'][] = [
                'o:item_set' => ['o:id' => $itemSetId]
            ];

            $addedCount++;
        }
        
        // Update the site with new item sets
        if ($addedCount > 0) {
            // Make sure we're only sending the site item set data
            $siteUpdateData = [
                'o:site_item_set' => $updatedSiteData['o:site_item_set']
            ];
            
            $api->update('sites', $siteId, $siteUpdateData, [], ['isPartial' => true]);
            echo "    Added $addedCount item sets to site (ID: $siteId)\n";
        }
        
        return $addedCount;
    } catch (Exception $e) {
        echo "    Error adding item sets to site: " . $e->getMessage() . "\n";
        return 0;
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
        $data = $site->jsonSerialize();

        // Contar site_item_set
        $counts['itemSetsCount'] = isset($data['o:site_item_set']) ? count($data['o:site_item_set']) : 0;
        
        // Get items count for the site
        $itemsResponse = $api->search('items', ['site_id' => $siteId]);
        $counts['itemsCount'] = $itemsResponse->getTotalResults();

        // Get media count for the site
        $mediaResponse = $api->search('media', ['site_id' => $siteId]);
        $counts['mediaCount'] = $mediaResponse->getTotalResults();
        
        echo "    Site counts - Item Sets: " . $counts['itemSetsCount'] . ", Items: " . $counts['itemsCount'] . ", Media: " . $counts['mediaCount'] . "\n";
    } catch (Exception $e) {
        echo "    Error getting item counts: " . $e->getMessage() . "\n";
    }
    
    return $counts;
}
/**
 * Prepare an ItemSetRepresentation for safe update.
 *
 * @param \Omeka\Api\Representation\ItemSetRepresentation $itemSet
 * @return array Cleaned array for update
 */
function cleanItemSetForUpdate(\Omeka\Api\Representation\ItemSetRepresentation $itemSet): array
{
    $data = $itemSet->jsonSerialize();

    // Remove read-only/system keys
    unset(
        $data['@context'],
        $data['@id'],
        $data['@type'],
        $data['o:id'],
        $data['o:owner'],
        $data['o:created'],
        $data['o:modified'],
        $data['o:items'],
        $data['o:thumbnail'],
        $data['thumbnail_display_urls']
    );

    return $data;
}

/**
 * Add site_id to user's default_item_sites array in user settings.
 * Avoids duplicates by checking if the site is already in the array.
 *
 * @param int $userId The ID of the user
 * @param int $siteId The ID of the site to add
 * @param ApiManager $api The Omeka API manager
 * @param EntityManager $entityManager The Doctrine entity manager
 * @return bool True if successful, false otherwise
 */
function addSiteToUserDefaultItemSites($userId, $siteId, $api, $entityManager) {
    try {
        echo "    Adding site (ID: $siteId) to user's (ID: $userId) default_item_sites...\n";
        
        // Get the user entity directly from the entity manager
        $userEntity = $entityManager->find('Omeka\Entity\User', $userId);
        
        if (!$userEntity) {
            echo "    Error: User not found: $userId\n";
            return false;
        }
        
        // Get current user settings
        $settings = $userEntity->getSettings();
        
        // Get current default_item_sites array or initialize as empty array
        $defaultItemSites = isset($settings['default_item_sites']) ? $settings['default_item_sites'] : [];
        
        // Ensure it's an array
        if (!is_array($defaultItemSites)) {
            $defaultItemSites = [];
        }
        
        // Check if site_id is already in the array to avoid duplicates
        if (in_array($siteId, $defaultItemSites)) {
            echo "    Site (ID: $siteId) already in user's default_item_sites. No update needed.\n";
            return true;
        }
        
        // Add the site_id to the array
        $defaultItemSites[] = $siteId;
        
        // Update the settings
        $settings['default_item_sites'] = $defaultItemSites;
        $userEntity->setSettings($settings);
        
        // Persist the changes
        $entityManager->flush();
        
        echo "    Successfully added site (ID: $siteId) to user's (ID: $userId) default_item_sites.\n";
        echo "    User's default_item_sites now contains: " . implode(', ', $defaultItemSites) . "\n";
        
        return true;
    } catch (Exception $e) {
        echo "    Error adding site to user's default_item_sites: " . $e->getMessage() . "\n";
        return false;
    }
}
