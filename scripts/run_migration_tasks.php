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
 *   php run_migration_tasks.php --input-file <input_file> --output-file <output_file> [--delete-tasks] [--omeka-path <path>] [--config-site-file <config_file>] [--default-nav] [--base-url <url>]
 *
 * Arguments:
 *   --input-file         Path to the input JSON file with migration tasks information
 *   --output-file        Path to the output JSON file to write the updated information
 *   --delete-tasks       Delete the original tasks after execution (optional)
 *   --omeka-path         Path to the Omeka S installation (default: /var/www/html)
 *   --config-site-file   Path to a JSON file with site settings to apply to all sites (optional)
 *   --default-nav        Configure default navigation for all sites (optional)
 *   --base-url           Base URL of the Omeka installation (required with --default-nav, e.g., http://localhost:8888)
 *
 * Author: [Your Name]
 * Date: 26-08-2025
 */

// Define constants
define('SCRIPT_VERSION', '1.0.0');

// Parse command line arguments
$options = getopt('', ['input-file:', 'output-file:', 'delete-tasks', 'omeka-path:', 'config-site-file:', 'default-nav', 'base-url:']);

// Validate required arguments
if (!isset($options['input-file']) || !isset($options['output-file'])) {
    echo "Error: Missing required arguments.\n";
    echo "Usage: php run_migration_tasks.php --input-file <input_file> --output-file <output_file> [--delete-tasks] [--omeka-path <path>] [--config-site-file <config_file>] [--default-nav] [--base-url <url>]\n";
    exit(1);
}

$inputFile = $options['input-file'];
$outputFile = $options['output-file'];
$deleteTasks = isset($options['delete-tasks']);
$omekaPath = isset($options['omeka-path']) ? $options['omeka-path'] : '/var/www/html';
$configSiteFile = isset($options['config-site-file']) ? $options['config-site-file'] : null;
$defaultNav = isset($options['default-nav']);
$baseUrl = isset($options['base-url']) ? $options['base-url'] : 'http://localhost:8888';

// Validate that base-url is provided when default-nav is requested
if ($defaultNav && !isset($options['base-url'])) {
    echo "Warning: --base-url not provided, using default: $baseUrl\n";
}

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

// Read and validate config site file if provided
$siteConfig = null;
if ($configSiteFile) {
    if (!file_exists($configSiteFile)) {
        echo "Error: Config site file not found: $configSiteFile\n";
        exit(1);
    }

    echo "Reading config site file: $configSiteFile\n";
    $configContent = file_get_contents($configSiteFile);
    $siteConfig = json_decode($configContent, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        echo "Error: Invalid JSON in config site file: " . json_last_error_msg() . "\n";
        exit(1);
    }

    if (!isset($siteConfig['site_data'])) {
        echo "Error: Config site file must contain 'site_data' key\n";
        exit(1);
    }
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
        addSiteToUserDefaultItemSites($userId, $siteId, $serviceLocator);
    }

    // Get item sets and items count for the site
    $counts = getItemCounts($siteId, $api);

    // Add counts to the channel data
    $channel['omeka_itemsets_count'] = $counts['itemSetsCount'];
    $channel['omeka_items_count'] = $counts['itemsCount'];
    $channel['omeka_media_count'] = $counts['mediaCount'];

    // Apply site configuration if provided
    if ($siteConfig) {
        applySiteConfiguration($siteId, $siteConfig, $api, $serviceLocator, $entityManager);
    }

    // Configure default navigation if requested
    if ($defaultNav) {
        // Get the site to extract slug
        $site = $api->read('sites', $siteId)->getContent();
        $siteSlug = $site->slug();

        // Create redirect page using the provided base URL
        $pageId = createRedirectPage($siteId, $siteSlug, $baseUrl, $api);

        // Configure navigation if page was created successfully
        if ($pageId) {
            configureDefaultNavigation($siteId, $pageId, $api);
        }
    }

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
 * @param ServiceLocatorInterface $serviceLocator The service locator
 * @return bool True if successful, false otherwise
 */
function addSiteToUserDefaultItemSites($userId, $siteId, $serviceLocator) {
    try {
        echo "    Adding site (ID: $siteId) to user's (ID: $userId) default_item_sites...\n";

        // Get the UserSettings service
        $userSettings = $serviceLocator->get('Omeka\Settings\User');

        // Get the entity manager to find the user
        $entityManager = $serviceLocator->get('Omeka\EntityManager');
        $userEntity = $entityManager->find('Omeka\Entity\User', $userId);

        if (!$userEntity) {
            echo "    Error: User not found: $userId\n";
            return false;
        }

        // Set the target user for user settings
        $userSettings->setTargetId($userId);

        // Get current default_item_sites array or initialize as empty array
        $defaultItemSites = $userSettings->get('default_item_sites', []);

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

        // Update the settings using the UserSettings service
        $userSettings->set('default_item_sites', $defaultItemSites);

        echo "    Successfully added site (ID: $siteId) to user's (ID: $userId) default_item_sites.\n";
        echo "    User's default_item_sites now contains: " . implode(', ', $defaultItemSites) . "\n";

        return true;
    } catch (Exception $e) {
        echo "    Error adding site to user's default_item_sites: " . $e->getMessage() . "\n";
        return false;
    }
}

/**
 * Apply site configuration from the config JSON to a site.
 * Sets site theme, site settings, and theme settings.
 *
 * @param int $siteId The ID of the site
 * @param array $siteConfig The site configuration data from JSON
 * @param ApiManager $api The Omeka API manager
 * @param ServiceLocatorInterface $serviceLocator The service locator
 * @param EntityManager $entityManager The Doctrine entity manager
 * @return bool True if successful, false otherwise
 */
function applySiteConfiguration($siteId, $siteConfig, $api, $serviceLocator, $entityManager) {
    try {
        echo "    Applying site configuration to site (ID: $siteId)...\n";

        if (!isset($siteConfig['site_data'])) {
            echo "    Error: No 'site_data' found in configuration\n";
            return false;
        }

        $siteData = $siteConfig['site_data'];

        // Get the site entity
        $siteEntity = $entityManager->find('Omeka\Entity\Site', $siteId);
        if (!$siteEntity) {
            echo "    Error: Site not found: $siteId\n";
            return false;
        }

        // Apply site theme if provided - do this FIRST before settings
        if (isset($siteData['site']['theme'])) {
            $theme = $siteData['site']['theme'];
            echo "    Setting theme: $theme\n";

            // Use API to update the theme
            $api->update('sites', $siteId, ['o:theme' => $theme], [], ['isPartial' => true]);

            // Flush and clear entity manager to ensure theme change is persisted
            $entityManager->flush();
            $entityManager->clear();

            echo "    Theme updated and changes persisted\n";
        }

        // Get the Site Settings service AFTER theme is set
        $siteSettings = $serviceLocator->get('Omeka\Settings\Site');
        $siteSettings->setTargetId($siteId);

        // Apply site settings if provided
        if (isset($siteData['site_settings']) && is_array($siteData['site_settings'])) {
            echo "    Applying " . count($siteData['site_settings']) . " site settings...\n";
            foreach ($siteData['site_settings'] as $key => $value) {
                $siteSettings->set($key, $value);
                echo "      - Set $key\n";
            }
        }

        // Apply theme settings if provided
        // Theme settings in Omeka are stored with keys prefixed by theme name
        // For example: "freedom-ate_resource_tags", "freedom-ate_browse_layout"
        $themeSettingsApplied = 0;
        foreach ($siteData as $key => $value) {
            if (strpos($key, 'theme_settings_') === 0) {
                $themeName = substr($key, 15); // Remove 'theme_settings_' prefix (e.g., "freedom-ate")
                echo "    Applying theme settings for theme: $themeName\n";

                if (is_array($value)) {
                    $prefixedKey = 'theme_settings_'.$themeName;
                    
                    // Opción 1: Reemplazar todos los settings del tema
                    $siteSettings->set($prefixedKey, $value);
                    $themeSettingsApplied++;
              
                    // O si quieres ver cada setting individualmente:
                    foreach ($value as $setting => $valor) {
                        echo "      - Setting: $setting = " . json_encode($valor) . "\n";
                    }
                }
            }
        }

        if ($themeSettingsApplied > 0) {
            echo "    Applied $themeSettingsApplied theme settings\n";
        }

        echo "    Site configuration applied successfully\n";
        return true;
    } catch (Exception $e) {
        echo "    Error applying site configuration: " . $e->getMessage() . "\n";
        echo "    Stack trace: " . $e->getTraceAsString() . "\n";
        return false;
    }
}

/**
 * Create a redirect page that redirects to the site's item browse page.
 * This page will be used as the homepage.
 *
 * @param int $siteId The ID of the site
 * @param string $siteSlug The slug of the site
 * @param string $baseUrl The base URL of the Omeka installation
 * @param ApiManager $api The Omeka API manager
 * @return int|null The page ID if successful, null otherwise
 */
function createRedirectPage($siteId, $siteSlug, $baseUrl, $api) {
    try {
        echo "    Creating redirect page for site (ID: $siteId)...\n";

        // Build the redirect URL
        $redirectUrl = rtrim($baseUrl, '/') . "/s/$siteSlug/item";

        // Prepare the page data
        $pageData = [
            'o:slug' => 'item',
            'o:title' => 'Inicio',
            'o:is_public' => true,
            'o:site' => ['o:id' => $siteId],
            'o:block' => [
                [
                    'o:layout' => 'redirectToUrl',
                    'o:data' => [
                        'url' => $redirectUrl
                    ],
                    'o:layout_data' => [
                        'grid_column_position' => 'auto',
                        'grid_column_span' => '12'
                    ]
                ]
            ]
        ];

        // Check if a page with slug 'item' already exists
        $existingPages = $api->search('site_pages', [
            'site_id' => $siteId,
            'slug' => 'item'
        ])->getContent();

        if (!empty($existingPages)) {
            // Update the existing page
            $existingPage = reset($existingPages);
            $pageId = $existingPage->id();
            echo "    Updating existing redirect page (ID: $pageId)...\n";
            $api->update('site_pages', $pageId, $pageData, [], ['isPartial' => true]);
        } else {
            // Create a new page
            $response = $api->create('site_pages', $pageData);
            $page = $response->getContent();
            $pageId = $page->id();
            echo "    Created redirect page (ID: $pageId)\n";
        }

        return $pageId;
    } catch (Exception $e) {
        echo "    Error creating redirect page: " . $e->getMessage() . "\n";
        return null;
    }
}

/**
 * Configure default navigation for a site.
 * Sets up navigation with a redirect page as homepage and browse item sets.
 *
 * @param int $siteId The ID of the site
 * @param int $pageId The ID of the redirect page
 * @param ApiManager $api The Omeka API manager
 * @return bool True if successful, false otherwise
 */
function configureDefaultNavigation($siteId, $pageId, $api) {
    try {
        echo "    Configuring default navigation for site (ID: $siteId)...\n";

        // Prepare the navigation structure
        $navigationData = [
            [
                'type' => 'page',
                'data' => [
                    'label' => '',
                    'id' => $pageId,
                    'is_public' => true
                ],
                'links' => []
            ],
            [
                'type' => 'browseItemSets',
                'data' => [
                    'label' => '',
                    'query' => ''
                ],
                'links' => []
            ]
        ];

        // Update the site with the new navigation
        $siteUpdateData = [
            'o:navigation' => $navigationData,
            'o:homepage' => ['o:id' => $pageId]
        ];

        $api->update('sites', $siteId, $siteUpdateData, [], ['isPartial' => true]);

        echo "    Default navigation configured successfully\n";
        return true;
    } catch (Exception $e) {
        echo "    Error configuring default navigation: " . $e->getMessage() . "\n";
        return false;
    }
}
