#!/usr/bin/env php
<?php
/**
 * Update Disk Quota Script
 *
 * This script sets the disk quota setting for one or more Omeka S users and/or
 * sites based on CSV files. Each row in the CSV carries its own quota value, so
 * different users/sites can receive different quotas in the same run.
 *
 * Purpose:
 *   - Set the 'diskquota_user_quota' user setting from a users CSV
 *   - Set the 'diskquota_site_quota' site setting from a sites CSV
 *   - Show how many users/sites will be changed and require confirmation before proceeding
 *
 * Usage:
 *   php update_disk_quota.php [--users-file <users.csv>] [--sites-file <sites.csv>] [--omeka-path <path>]
 *
 * Arguments:
 *   --users-file      Path to CSV file with 'user_id,diskquota_user_quota' columns (optional)
 *   --sites-file      Path to CSV file with 'site_id,diskquota_site_quota' columns (optional)
 *   --omeka-path      Path to the Omeka S installation (default: /var/www/html)
 *
 * Notes:
 *   - At least one of --users-file or --sites-file must be provided (both may be used together)
 *   - The script prints how many users/sites will be updated and asks for confirmation
 *     (typing 'yes') before applying any change
 *
 * Author: ATE - Área de Tecnología Educativa
 * Date: 2026-08-27
 */

// Define constants
define('SCRIPT_VERSION', '1.0.0');

// Parse command line arguments
$options = getopt('', ['users-file:', 'sites-file:', 'omeka-path:']);

// Validate that at least one of --users-file / --sites-file is provided
if (!isset($options['users-file']) && !isset($options['sites-file'])) {
    echo "Error: At least one of --users-file or --sites-file must be provided.\n";
    echo "Usage: php update_disk_quota.php [--users-file <users.csv>] [--sites-file <sites.csv>] [--omeka-path <path>]\n";
    exit(1);
}

$usersFile = isset($options['users-file']) ? $options['users-file'] : null;
$sitesFile = isset($options['sites-file']) ? $options['sites-file'] : null;
$omekaPath = isset($options['omeka-path']) ? $options['omeka-path'] : '/var/www/html';

echo "===========================================\n";
echo "Update Disk Quota Script\n";
echo "Version: " . SCRIPT_VERSION . "\n";
echo "===========================================\n";

// Validate and read users CSV
$userQuotas = [];
if ($usersFile !== null) {
    if (!file_exists($usersFile)) {
        echo "Error: Users file not found: $usersFile\n";
        exit(1);
    }

    echo "Reading users file: $usersFile\n";
    $userQuotas = readQuotasFromCsv($usersFile, 'user_id', 'diskquota_user_quota');

    if (empty($userQuotas)) {
        echo "Error: No valid rows found in users CSV (expected columns 'user_id,diskquota_user_quota')\n";
        exit(1);
    }
}

// Validate and read sites CSV
$siteQuotas = [];
if ($sitesFile !== null) {
    if (!file_exists($sitesFile)) {
        echo "Error: Sites file not found: $sitesFile\n";
        exit(1);
    }

    echo "Reading sites file: $sitesFile\n";
    $siteQuotas = readQuotasFromCsv($sitesFile, 'site_id', 'diskquota_site_quota');

    if (empty($siteQuotas)) {
        echo "Error: No valid rows found in sites CSV (expected columns 'site_id,diskquota_site_quota')\n";
        exit(1);
    }
}

// Show summary and ask for confirmation before touching anything
echo "-------------------------------------------\n";
echo "SUMMARY OF CHANGES TO APPLY\n";
echo "-------------------------------------------\n";
echo count($userQuotas) . " user(s) will have 'diskquota_user_quota' updated\n";
echo count($siteQuotas) . " site(s) will have 'diskquota_site_quota' updated\n";
echo "-------------------------------------------\n";
echo "Type 'yes' to proceed: ";

$handle = fopen("php://stdin", "r");
$confirmation = trim(fgets($handle));
fclose($handle);

if ($confirmation !== 'yes') {
    echo "Operation cancelled. Confirmation not received.\n";
    exit(0);
}

echo "Confirmation received. Proceeding...\n\n";

// Initialize Omeka S application
echo "Initializing Omeka S application...\n";
require_once "$omekaPath/bootstrap.php";

$application    = Omeka\Mvc\Application::init(require "$omekaPath/application/config/application.config.php");
$serviceLocator = $application->getServiceManager();
$entityManager  = $serviceLocator->get('Omeka\EntityManager');
$api            = $serviceLocator->get('Omeka\ApiManager');

// Authenticate as admin (ID 1) for API operations
$auth      = $serviceLocator->get('Omeka\AuthenticationService');
$adminUser = $entityManager->find('Omeka\Entity\User', 1);
if ($adminUser) {
    $auth->getStorage()->write($adminUser);
    echo "Using admin user for API operations\n";
} else {
    echo "Warning: Admin user not found. Some operations may fail due to permission issues.\n";
}

$userSettings = $serviceLocator->get('Omeka\Settings\User');
$siteSettings = $serviceLocator->get('Omeka\Settings\Site');

$userSuccessCount = 0;
$userFailureCount = 0;
$siteSuccessCount = 0;
$siteFailureCount = 0;

// Process users
if (!empty($userQuotas)) {
    $totalUsers = count($userQuotas);
    echo "\nProcessing $totalUsers user(s)...\n";
    echo "========================================\n";

    $index = 0;
    foreach ($userQuotas as $userId => $quota) {
        $index++;
        echo "\n[$index/$totalUsers] Processing user ID: $userId (diskquota_user_quota: $quota)\n";

        if (setUserDiskQuota($userId, $quota, $userSettings, $entityManager)) {
            echo "  ✓ User $userId updated successfully\n";
            $userSuccessCount++;
        } else {
            $userFailureCount++;
        }
    }
}

// Process sites
if (!empty($siteQuotas)) {
    $totalSites = count($siteQuotas);
    echo "\nProcessing $totalSites site(s)...\n";
    echo "========================================\n";

    $index = 0;
    foreach ($siteQuotas as $siteId => $quota) {
        $index++;
        echo "\n[$index/$totalSites] Processing site ID: $siteId (diskquota_site_quota: $quota)\n";

        if (setSiteDiskQuota($siteId, $quota, $siteSettings, $api)) {
            echo "  ✓ Site $siteId updated successfully\n";
            $siteSuccessCount++;
        } else {
            $siteFailureCount++;
        }
    }
}

// Summary
echo "\n===========================================\n";
echo "SUMMARY\n";
echo "===========================================\n";
echo "Users  - processed: " . count($userQuotas) . ", successful: $userSuccessCount, failed: $userFailureCount\n";
echo "Sites  - processed: " . count($siteQuotas) . ", successful: $siteSuccessCount, failed: $siteFailureCount\n";
echo "\nScript completed.\n";

exit(($userFailureCount > 0 || $siteFailureCount > 0) ? 1 : 0);

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Read an ID column and a quota column from a CSV file.
 *
 * @param string $csvFile   Path to the CSV file
 * @param string $idColumn  Name of the ID column (e.g. 'user_id', 'site_id')
 * @param string $quotaColumn Name of the quota column (e.g. 'diskquota_user_quota')
 * @return array Map of id => quota (both int)
 */
function readQuotasFromCsv($csvFile, $idColumn, $quotaColumn) {
    $quotas = [];

    $handle = fopen($csvFile, 'r');
    if (!$handle) {
        echo "Error: Could not open CSV file: $csvFile\n";
        return [];
    }

    $header = fgetcsv($handle);
    if (!$header) {
        echo "Error: CSV file is empty or invalid\n";
        fclose($handle);
        return [];
    }

    $idIndex = array_search($idColumn, $header);
    $quotaIndex = array_search($quotaColumn, $header);

    if ($idIndex === false || $quotaIndex === false) {
        echo "Error: CSV file must have '$idColumn' and '$quotaColumn' columns\n";
        fclose($handle);
        return [];
    }

    while (($row = fgetcsv($handle)) !== false) {
        if (!isset($row[$idIndex]) || !isset($row[$quotaIndex])) {
            continue;
        }
        if (!is_numeric($row[$idIndex]) || !is_numeric($row[$quotaIndex])) {
            echo "Warning: Skipping row with non-numeric $idIndex/$quotaColumn value: " . implode(',', $row) . "\n";
            continue;
        }
        $quotas[(int)$row[$idIndex]] = (int)$row[$quotaIndex];
    }

    fclose($handle);
    return $quotas;
}

/**
 * Set the 'diskquota_user_quota' user setting for a given user.
 *
 * @param int    $userId       The Omeka user ID
 * @param int    $quota        The quota value to set
 * @param object $userSettings The Omeka UserSettings service
 * @param object $entityManager The Doctrine entity manager
 * @return bool True if successful, false otherwise
 */
function setUserDiskQuota($userId, $quota, $userSettings, $entityManager) {
    try {
        $userEntity = $entityManager->find('Omeka\Entity\User', $userId);
        if (!$userEntity) {
            echo "  ERROR: User not found: $userId\n";
            return false;
        }

        $userSettings->setTargetId($userId);
        $userSettings->set('diskquota_user_quota', $quota);

        return true;
    } catch (Exception $e) {
        echo "  ERROR: Failed to set diskquota_user_quota for user $userId: " . $e->getMessage() . "\n";
        return false;
    }
}

/**
 * Set the 'diskquota_site_quota' site setting for a given site.
 *
 * @param int    $siteId       The Omeka site ID
 * @param int    $quota        The quota value to set
 * @param object $siteSettings The Omeka SiteSettings service
 * @param object $api          The Omeka API manager
 * @return bool True if successful, false otherwise
 */
function setSiteDiskQuota($siteId, $quota, $siteSettings, $api) {
    try {
        // Verify site exists
        $api->read('sites', $siteId);

        $siteSettings->setTargetId($siteId);
        $siteSettings->set('diskquota_site_quota', $quota);

        return true;
    } catch (Exception $e) {
        echo "  ERROR: Failed to set diskquota_site_quota for site $siteId: " . $e->getMessage() . "\n";
        return false;
    }
}
