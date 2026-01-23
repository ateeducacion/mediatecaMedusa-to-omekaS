#!/usr/bin/env php
<?php
/**
 * Update Site Settings Script
 *
 * This script updates site settings for one or more Omeka S sites based on a
 * configuration file. It allows updating specific sites listed in a CSV file
 * or all sites in the installation.
 *
 * Purpose:
 *   - Apply site configuration (theme, site settings, theme settings) to sites
 *   - Optionally configure default navigation with redirect page
 *   - Process single sites, multiple sites from CSV, or all sites
 *
 * Usage:
 *   php update_site_settings.php --config-file <config.json> [--sites-file <sites.csv>] [--all] [--default-nav] [--base-url <url>] [--omeka-path <path>]
 *
 * Arguments:
 *   --config-file     Path to JSON file with site configuration to apply (required)
 *   --sites-file      Path to CSV file with site_id column listing sites to update (optional)
 *   --all             Apply settings to ALL sites (requires confirmation, optional)
 *   --default-nav     Configure default navigation for sites (optional)
 *   --base-url        Base URL of the Omeka installation (required with --default-nav, e.g., http://localhost:8888)
 *   --omeka-path      Path to the Omeka S installation (default: /var/www/html)
 *
 * Notes:
 *   - Either --sites-file or --all must be provided
 *   - Using --all requires typing 'CHANGE ALL' for confirmation
 *   - The CSV file must have a 'site_id' column
 *   - Configuration file should contain 'site_data' key with settings
 *
 * Author: ATE Education
 * Date: 2025-12-16
 */

// Define constants
define('SCRIPT_VERSION', '1.0.0');

// Parse command line arguments
$options = getopt('', ['config-file:', 'sites-file:', 'all', 'default-nav', 'base-url:', 'omeka-path:']);

// Validate required arguments
if (!isset($options['config-file'])) {
    echo "Error: Missing required argument --config-file.\n";
    echo "Usage: php update_site_settings.php --config-file <config.json> [--sites-file <sites.csv>] [--all] [--default-nav] [--base-url <url>] [--omeka-path <path>]\n";
    exit(1);
}

// Check that either --sites-file or --all is provided
if (!isset($options['sites-file']) && !isset($options['all'])) {
    echo "Error: Either --sites-file or --all must be provided.\n";
    echo "Usage: php update_site_settings.php --config-file <config.json> [--sites-file <sites.csv>] [--all] [--default-nav] [--base-url <url>] [--omeka-path <path>]\n";
    exit(1);
}

// Check that both --sites-file and --all are not provided simultaneously
if (isset($options['sites-file']) && isset($options['all'])) {
    echo "Error: Cannot use both --sites-file and --all options. Choose one.\n";
    exit(1);
}

// Extract options
$configFile = $options['config-file'];
$sitesFile = isset($options['sites-file']) ? $options['sites-file'] : null;
$applyToAll = isset($options['all']);
$defaultNav = isset($options['default-nav']);
$baseUrl = isset($options['base-url']) ? $options['base-url'] : 'http://localhost:8888';
$omekaPath = isset($options['omeka-path']) ? $options['omeka-path'] : '/var/www/html';

// Validate base-url when default-nav is requested
if ($defaultNav && !isset($options['base-url'])) {
    echo "Warning: --base-url not provided, using default: $baseUrl\n";
}

// Validate config file
if (!file_exists($configFile)) {
    echo "Error: Config file not found: $configFile\n";
    exit(1);
}

// Read and validate config file
echo "Reading config file: $configFile\n";
$configContent = file_get_contents($configFile);
$siteConfig = json_decode($configContent, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    echo "Error: Invalid JSON in config file: " . json_last_error_msg() . "\n";
    exit(1);
}

if (!isset($siteConfig['site_data'])) {
    echo "Error: Config file must contain 'site_data' key\n";
    exit(1);
}

// Initialize site IDs array
$siteIds = [];

// If --all is used, prompt for confirmation
if ($applyToAll) {
    echo "\n========================================\n";
    echo "WARNING: You are about to apply settings to ALL sites!\n";
    echo "========================================\n";
    echo "Type 'CHANGE ALL' to confirm (case sensitive): ";

    // Read user input
    $handle = fopen("php://stdin", "r");
    $confirmation = trim(fgets($handle));
    fclose($handle);

    if ($confirmation !== 'CHANGE ALL') {
        echo "Operation cancelled. Confirmation not received.\n";
        exit(0);
    }

    echo "Confirmation received. Proceeding with all sites...\n\n";
} else {
    // Validate sites file
    if (!file_exists($sitesFile)) {
        echo "Error: Sites file not found: $sitesFile\n";
        exit(1);
    }

    // Read and parse CSV file
    echo "Reading sites file: $sitesFile\n";
    $siteIds = readSiteIdsFromCsv($sitesFile);

    if (empty($siteIds)) {
        echo "Error: No site IDs found in CSV file or invalid format\n";
        exit(1);
    }

    echo "Found " . count($siteIds) . " site(s) to process\n";
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

// If --all is used, get all site IDs from the database
if ($applyToAll) {
    echo "Retrieving all site IDs from database...\n";
    $siteIds = getAllSiteIds($api);
    echo "Found " . count($siteIds) . " total site(s) in the installation\n";
}

// Process each site
$totalSites = count($siteIds);
$successCount = 0;
$failureCount = 0;

echo "\nProcessing $totalSites site(s)...\n";
echo "========================================\n";

foreach ($siteIds as $index => $siteId) {
    $siteNumber = $index + 1;
    echo "\n[$siteNumber/$totalSites] Processing site ID: $siteId\n";

    try {
        // Verify site exists
        $site = $api->read('sites', $siteId)->getContent();
        $siteSlug = $site->slug();
        $siteTitle = $site->title();
        echo "  Site: $siteTitle (slug: $siteSlug)\n";

        // Apply site configuration
        $configResult = applySiteConfiguration($siteId, $siteConfig, $api, $serviceLocator, $entityManager);

        if (!$configResult) {
            echo "  ERROR: Failed to apply site configuration\n";
            $failureCount++;
            continue;
        }

        // Configure default navigation if requested
        if ($defaultNav) {
            // Create redirect page
            $pageId = createRedirectPage($siteId, $siteSlug, $baseUrl, $api);

            if ($pageId) {
                // Configure navigation with the created page
                $navResult = configureDefaultNavigation($siteId, $pageId, $api);

                if (!$navResult) {
                    echo "  WARNING: Site configuration applied but navigation configuration failed\n";
                }
            } else {
                echo "  WARNING: Site configuration applied but redirect page creation failed\n";
            }
        }

        echo "  ✓ Site updated successfully\n";
        $successCount++;

    } catch (Exception $e) {
        echo "  ERROR: " . $e->getMessage() . "\n";
        $failureCount++;
    }
}

// Summary
echo "\n========================================\n";
echo "SUMMARY\n";
echo "========================================\n";
echo "Total sites processed: $totalSites\n";
echo "Successful: $successCount\n";
echo "Failed: $failureCount\n";
echo "\nScript completed.\n";

exit(0);

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Read site IDs from a CSV file.
 * The CSV file must have a 'site_id' column.
 *
 * @param string $csvFile Path to the CSV file
 * @return array Array of site IDs
 */
function readSiteIdsFromCsv($csvFile) {
    $siteIds = [];

    // Open the CSV file
    $handle = fopen($csvFile, 'r');
    if (!$handle) {
        echo "Error: Could not open CSV file: $csvFile\n";
        return [];
    }

    // Read the header row
    $header = fgetcsv($handle);
    if (!$header) {
        echo "Error: CSV file is empty or invalid\n";
        fclose($handle);
        return [];
    }

    // Find the site_id column index
    $siteIdIndex = array_search('site_id', $header);
    if ($siteIdIndex === false) {
        echo "Error: CSV file must have a 'site_id' column\n";
        fclose($handle);
        return [];
    }

    // Read each row and extract site_id
    while (($row = fgetcsv($handle)) !== false) {
        if (isset($row[$siteIdIndex]) && is_numeric($row[$siteIdIndex])) {
            $siteIds[] = (int)$row[$siteIdIndex];
        }
    }

    fclose($handle);
    return $siteIds;
}

/**
 * Get all site IDs from the Omeka installation.
 *
 * @param ApiManager $api The Omeka API manager
 * @return array Array of site IDs
 */
function getAllSiteIds($api) {
    $siteIds = [];

    try {
        // Search for all sites
        $response = $api->search('sites', []);
        $sites = $response->getContent();

        // Extract site IDs
        foreach ($sites as $site) {
            $siteIds[] = $site->id();
        }
    } catch (Exception $e) {
        echo "Error retrieving sites: " . $e->getMessage() . "\n";
    }

    return $siteIds;
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

                    // Replace all theme settings
                    $siteSettings->set($prefixedKey, $value);
                    $themeSettingsApplied++;

                    // Log each setting individually
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
            // Update the existing page (use isPartial => false to replace all blocks)
            $existingPage = reset($existingPages);
            $pageId = $existingPage->id();
            echo "    Updating existing redirect page (ID: $pageId)...\n";
            $api->update('site_pages', $pageId, $pageData, [], ['isPartial' => false]);
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
                    'label' => 'Colecciones',
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
