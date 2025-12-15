#!/usr/bin/env php
<?php
/**
 * Read Site Settings Script
 *
 * This script reads all settings properties of an Omeka-S site,
 * including theme settings, and outputs them in JSON format.
 *
 * Usage:
 *   php read_site_settings.php --site-id <site_id> [--output-file <output_file>] [--omeka-path <path>]
 *
 * Arguments:
 *   --site-id        ID of the site to read settings from (required)
 *   --output-file    Path to output JSON file (optional, prints to stdout if not provided)
 *   --omeka-path     Path to the Omeka S installation (default: /var/www/html)
 *
 * Author: Generated Script
 * Date: 2025-12-14
 */

// Define constants
define('SCRIPT_VERSION', '1.0.0');

// Parse command line arguments
$options = getopt('', ['site-id:', 'output-file:', 'omeka-path:']);

// Validate required arguments
if (!isset($options['site-id'])) {
    echo "Error: Missing required argument --site-id.\n";
    echo "Usage: php read_site_settings.php --site-id <site_id> [--output-file <output_file>] [--omeka-path <path>]\n";
    exit(1);
}

$siteId = (int)$options['site-id'];
$outputFile = isset($options['output-file']) ? $options['output-file'] : null;
$omekaPath = isset($options['omeka-path']) ? $options['omeka-path'] : '/var/www/html';

// Validate Omeka path
if (!file_exists("$omekaPath/bootstrap.php")) {
    echo "Error: Omeka bootstrap not found at: $omekaPath/bootstrap.php\n";
    echo "Please specify the correct path using --omeka-path\n";
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
$adminUser = $entityManager->find('Omeka\Entity\User', 1); // Admin user (ID 1)
if ($adminUser) {
    $auth->getStorage()->write($adminUser);
    echo "Using admin user for API operations\n";
} else {
    echo "Warning: Admin user not found. Some operations may fail due to permission issues.\n";
}

echo "Reading site settings for Site ID: $siteId\n";

try {
    // Read site using API
    $site = $api->read('sites', $siteId)->getContent();

    if (!$site) {
        echo "Error: Site not found with ID: $siteId\n";
        exit(1);
    }

    // Get site data using direct database queries
    $siteData = getSiteCompleteData($site, $entityManager, $serviceLocator);

    // Format output
    $output = [
        'site_id' => $siteId,
        'timestamp' => date('Y-m-d H:i:s'),
        'site_data' => $siteData
    ];

    // Convert to JSON
    $jsonOutput = json_encode($output, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

    if (json_last_error() !== JSON_ERROR_NONE) {
        echo "Error: Failed to encode JSON: " . json_last_error_msg() . "\n";
        exit(1);
    }

    // Output results
    if ($outputFile) {
        file_put_contents($outputFile, $jsonOutput);
        echo "Site settings written to: $outputFile\n";
    } else {
        echo "\n" . str_repeat("=", 80) . "\n";
        echo "SITE SETTINGS\n";
        echo str_repeat("=", 80) . "\n";
        echo $jsonOutput . "\n";
    }

    echo "Site settings read successfully.\n";
    exit(0);

} catch (Exception $e) {
    echo "Error reading site settings: " . $e->getMessage() . "\n";
    echo "Stack trace:\n" . $e->getTraceAsString() . "\n";
    exit(1);
}

/**
 * Get complete site data including all properties and settings.
 *
 * @param \Omeka\Api\Representation\SiteRepresentation $site The site representation
 * @param \Doctrine\ORM\EntityManager $entityManager The entity manager
 * @param \Laminas\ServiceManager\ServiceLocatorInterface $serviceLocator The service locator
 * @return array Complete site data
 */
function getSiteCompleteData($site, $entityManager, $serviceLocator) {
    // Get basic site data from JSON serialization
    $siteData = $site->jsonSerialize();

    // Remove context and type metadata for cleaner output
    $cleanData = $siteData;

    // Get site entity for additional properties
    $siteEntity = $entityManager->find('Omeka\Entity\Site', $site->id());

    if ($siteEntity) {
        // Add theme information from site entity
        $themeName = $siteEntity->getTheme();
        $cleanData['theme'] = $themeName;

        // Get all site settings from database
        echo "Reading site settings from database...\n";
        $allSettings = getAllSiteSettingsFromDatabase($site->id(), $entityManager);

        // Separate theme settings from general site settings
        echo "Separating theme settings...\n";
        $settingsData = separateThemeSettings($allSettings, $themeName);

        $cleanData['settings'] = $settingsData['site_settings'];
        $cleanData['theme_settings'] = $settingsData['theme_settings'];

        // Additional site properties
        $cleanData['is_public'] = $siteEntity->isPublic();
        $cleanData['assign_new_items'] = $siteEntity->getAssignNewItems();

        // Get navigation (already in jsonSerialize but ensure it's there)
        if (method_exists($siteEntity, 'getNavigation')) {
            $navigation = $siteEntity->getNavigation();
            $cleanData['navigation_raw'] = $navigation;
        }

        // Get item pool
        if (method_exists($siteEntity, 'getItemPool')) {
            $itemPool = $siteEntity->getItemPool();
            $cleanData['item_pool'] = $itemPool;
        }
    }

    // Organize data into logical sections
    $organizedData = [
        'site' => [
            'id' => $cleanData['o:id'] ?? null,
            'slug' => $cleanData['o:slug'] ?? null,
            'title' => $cleanData['o:title'] ?? null,
            'theme' => $cleanData['theme'] ?? null,
        ],
        'basic_info' => [
            'summary' => $cleanData['o:summary'] ?? null,
            'is_public' => $cleanData['is_public'] ?? null,
            'assign_new_items' => $cleanData['assign_new_items'] ?? null,
            'created' => $cleanData['o:created'] ?? null,
            'modified' => $cleanData['o:modified'] ?? null,
            'owner' => $cleanData['o:owner'] ?? null,
        ],
        'site_settings' => $cleanData['settings'] ?? [],
        'theme_settings' => $cleanData['theme_settings'] ?? [],
        'item_pool' => $cleanData['item_pool'] ?? [],
        'site_pages' => $cleanData['o:site_page'] ?? [],
        'site_item_sets' => $cleanData['o:site_item_set'] ?? [],
        'navigation' => $cleanData['o:navigation'] ?? [],
        'navigation_raw' => $cleanData['navigation_raw'] ?? null,
    ];

    return $organizedData;
}

/**
 * Get all site settings directly from the database.
 *
 * @param int $siteId The site ID
 * @param \Doctrine\ORM\EntityManager $entityManager The entity manager
 * @return array All site settings (key => value)
 */
function getAllSiteSettingsFromDatabase($siteId, $entityManager) {
    try {
        // Query the site_setting table for all settings of this site
        $connection = $entityManager->getConnection();
        $stmt = $connection->prepare('SELECT id, value FROM site_setting WHERE site_id = :site_id');
        $stmt->bindValue('site_id', $siteId);
        $result = $stmt->executeQuery();
        $settingsData = $result->fetchAllAssociative();

        $allSettings = [];
        foreach ($settingsData as $setting) {
            // Try to decode the value - Omeka-S can store settings in different formats
            $value = decodeSettingValue($setting['value']);
            $allSettings[$setting['id']] = $value;
        }

        echo "    Found " . count($allSettings) . " settings in database\n";
        return $allSettings;
    } catch (Exception $e) {
        echo "    Error: Could not retrieve settings from database: " . $e->getMessage() . "\n";
        return [];
    }
}

/**
 * Separate theme settings from general site settings.
 * Theme settings typically have keys that start with the theme name or contain specific patterns.
 *
 * @param array $allSettings All site settings
 * @param string $themeName The name of the active theme
 * @return array Array with 'site_settings' and 'theme_settings'
 */
function separateThemeSettings($allSettings, $themeName) {
    $siteSettings = [];
    $themeSettings = [];

    foreach ($allSettings as $key => $value) {
        // Check if this setting belongs to the theme
        // Common patterns:
        // - {theme_name}_{setting}
        // - Keys containing 'theme', 'color', 'logo', 'banner', 'footer', 'header'
        // - Any key that starts with the theme name

        $isThemeSetting = false;

        // Check if key starts with theme name
        if ($themeName && strpos($key, $themeName) === 0) {
            $isThemeSetting = true;
        }
        // Check for common theme-related keywords
        else if (preg_match('/(theme|color|logo|banner|footer|header|nav|menu|style|css|font|layout)/i', $key)) {
            $isThemeSetting = true;
        }

        if ($isThemeSetting) {
            $themeSettings[$key] = $value;
        } else {
            $siteSettings[$key] = $value;
        }
    }

    echo "    Separated into " . count($siteSettings) . " site settings and " . count($themeSettings) . " theme settings\n";

    return [
        'site_settings' => $siteSettings,
        'theme_settings' => $themeSettings
    ];
}

/**
 * Decode a setting value from the database.
 * Tries JSON first, then PHP unserialize, then returns raw value.
 *
 * @param string $value The raw value from database
 * @return mixed The decoded value
 */
function decodeSettingValue($value) {
    // Try JSON decode first (most common in modern Omeka-S)
    $jsonDecoded = json_decode($value, true);
    if (json_last_error() === JSON_ERROR_NONE) {
        return $jsonDecoded;
    }

    // Try PHP unserialize (older Omeka-S versions)
    $unserialized = @unserialize($value);
    if ($unserialized !== false || $value === 'b:0;') {
        return $unserialized;
    }

    // Return raw value if both fail (simple strings, numbers, etc.)
    return $value;
}

