#!/usr/bin/env php
<?php
/**
 * Report Disk Usage Script
 *
 * This script reports, for every Omeka S user and every site, the disk space
 * currently used and the disk quota currently in effect. The output is written
 * to two CSV files (one for users, one for sites) that can be edited and fed
 * back into update_disk_quota.php.
 *
 * Purpose:
 *   - Compute the used disk space per user and per site, using the same rules
 *     as the DiskQuota module (DiskQuota\Service\DiskQuotaManager):
 *       * User: sum of media.size of media owned by the user (has_original = 1)
 *       * Site: sum of media.size of items assigned to the site (item_site)
 *               + sum of media.size of items in item sets assigned to the site
 *               (site_item_set). An item reachable both ways is counted twice,
 *               exactly as the module does when enforcing the quota.
 *   - Read the current 'diskquota_user_quota' / 'diskquota_site_quota' setting,
 *     falling back to the global default when it is not set
 *
 * Usage:
 *   php report_disk_usage.php [--users-output <users.csv>] [--sites-output <sites.csv>] [--omeka-path <path>]
 *
 * Arguments:
 *   --users-output    Path of the users CSV to write (default: users_disk_usage.csv)
 *   --sites-output    Path of the sites CSV to write (default: sites_disk_usage.csv)
 *   --omeka-path      Path to the Omeka S installation (default: /var/www/html)
 *
 * Notes:
 *   - Quotas are expressed in MB (as stored by the DiskQuota module); usage is
 *     reported both in bytes and in MB. A quota <= 0 means unlimited.
 *   - The script is read-only: it does not change any setting.
 *
 * Author: ATE - Área de Tecnología Educativa
 * Date: 2026-09-21
 */

// Define constants
define('SCRIPT_VERSION', '1.0.0');
define('BYTES_PER_MB', 1024 * 1024);
// Fallback defaults used by DiskQuotaManager when the global setting is missing
define('DEFAULT_USER_QUOTA_MB', 500);
define('DEFAULT_SITE_QUOTA_MB', 1000);

// Parse command line arguments
$options = getopt('', ['users-output:', 'sites-output:', 'omeka-path:']);

$usersOutput = isset($options['users-output']) ? $options['users-output'] : 'users_disk_usage.csv';
$sitesOutput = isset($options['sites-output']) ? $options['sites-output'] : 'sites_disk_usage.csv';
$omekaPath   = isset($options['omeka-path']) ? $options['omeka-path'] : '/var/www/html';

echo "===========================================\n";
echo "Report Disk Usage Script\n";
echo "Version: " . SCRIPT_VERSION . "\n";
echo "===========================================\n";

// Validate Omeka path
if (!file_exists("$omekaPath/bootstrap.php")) {
    echo "Error: Omeka bootstrap not found at: $omekaPath/bootstrap.php\n";
    echo "Please specify the correct path using --omeka-path\n";
    exit(1);
}

// Initialize Omeka S application
echo "Initializing Omeka S application...\n";
require_once "$omekaPath/bootstrap.php";

$application    = Omeka\Mvc\Application::init(require "$omekaPath/application/config/application.config.php");
$serviceLocator = $application->getServiceManager();
$connection     = $serviceLocator->get('Omeka\Connection');
$globalSettings = $serviceLocator->get('Omeka\Settings');

$defaultUserQuota = $globalSettings->get('diskquota_default_user_quota', DEFAULT_USER_QUOTA_MB);
$defaultSiteQuota = $globalSettings->get('diskquota_default_site_quota', DEFAULT_SITE_QUOTA_MB);

echo "Default user quota: $defaultUserQuota MB\n";
echo "Default site quota: $defaultSiteQuota MB\n";

try {
    // Users
    echo "\nCollecting user disk usage...\n";
    $userRows = buildUserRows($connection, $defaultUserQuota);
    writeCsv($usersOutput, [
        'user_id', 'email', 'name', 'role', 'is_active',
        'used_bytes', 'used_mb', 'diskquota_user_quota', 'quota_source', 'usage_percent',
    ], $userRows);
    echo "  ✓ " . count($userRows) . " user(s) written to $usersOutput\n";

    // Sites
    echo "\nCollecting site disk usage...\n";
    $siteRows = buildSiteRows($connection, $defaultSiteQuota);
    writeCsv($sitesOutput, [
        'site_id', 'slug', 'title', 'owner_email',
        'used_bytes', 'used_mb', 'diskquota_site_quota', 'quota_source', 'usage_percent',
    ], $siteRows);
    echo "  ✓ " . count($siteRows) . " site(s) written to $sitesOutput\n";
} catch (Exception $e) {
    echo "ERROR: " . $e->getMessage() . "\n";
    exit(1);
}

echo "\nScript completed.\n";
exit(0);

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Build one CSV row per user with used space and effective quota.
 *
 * @param object $connection       The Doctrine DBAL connection
 * @param mixed  $defaultQuota     Global default user quota (MB)
 * @return array List of rows (associative arrays)
 */
function buildUserRows($connection, $defaultQuota) {
    $usage = fetchKeyValue($connection, '
        SELECT r.owner_id, COALESCE(SUM(m.size), 0)
        FROM media m
        JOIN resource r ON m.id = r.id
        WHERE r.owner_id IS NOT NULL AND m.has_original = 1
        GROUP BY r.owner_id
    ');

    $quotas = fetchSettings($connection, 'user_setting', 'user_id', 'diskquota_user_quota');

    $users = $connection->fetchAllAssociative(
        'SELECT id, email, name, role, is_active FROM user ORDER BY id'
    );

    $rows = [];
    foreach ($users as $user) {
        $userId = (int)$user['id'];
        $used   = isset($usage[$userId]) ? (int)$usage[$userId] : 0;
        $hasOwn = array_key_exists($userId, $quotas);
        $quota  = $hasOwn ? $quotas[$userId] : $defaultQuota;

        $rows[] = [
            'user_id'              => $userId,
            'email'                => $user['email'],
            'name'                 => $user['name'],
            'role'                 => $user['role'],
            'is_active'            => (int)$user['is_active'],
            'used_bytes'           => $used,
            'used_mb'              => bytesToMb($used),
            'diskquota_user_quota' => $quota,
            'quota_source'         => $hasOwn ? 'user' : 'default',
            'usage_percent'        => usagePercent($used, $quota),
        ];
    }

    return $rows;
}

/**
 * Build one CSV row per site with used space and effective quota.
 *
 * @param object $connection       The Doctrine DBAL connection
 * @param mixed  $defaultQuota     Global default site quota (MB)
 * @return array List of rows (associative arrays)
 */
function buildSiteRows($connection, $defaultQuota) {
    // Media of items assigned directly to the site
    $fromItems = fetchKeyValue($connection, '
        SELECT si.site_id, COALESCE(SUM(m.size), 0)
        FROM media m
        JOIN item i ON m.item_id = i.id
        JOIN item_site si ON si.item_id = i.id
        WHERE m.has_original = 1
        GROUP BY si.site_id
    ');

    // Media of items belonging to item sets assigned to the site
    $fromItemSets = fetchKeyValue($connection, '
        SELECT sis.site_id, COALESCE(SUM(m.size), 0)
        FROM media m
        JOIN item i ON m.item_id = i.id
        JOIN item_item_set iis ON iis.item_id = i.id
        JOIN site_item_set sis ON sis.item_set_id = iis.item_set_id
        WHERE m.has_original = 1
        GROUP BY sis.site_id
    ');

    $quotas = fetchSettings($connection, 'site_setting', 'site_id', 'diskquota_site_quota');

    $sites = $connection->fetchAllAssociative('
        SELECT s.id, s.slug, s.title, u.email AS owner_email
        FROM site s
        LEFT JOIN user u ON u.id = s.owner_id
        ORDER BY s.id
    ');

    $rows = [];
    foreach ($sites as $site) {
        $siteId = (int)$site['id'];
        $used   = (isset($fromItems[$siteId]) ? (int)$fromItems[$siteId] : 0)
                + (isset($fromItemSets[$siteId]) ? (int)$fromItemSets[$siteId] : 0);
        $hasOwn = array_key_exists($siteId, $quotas);
        $quota  = $hasOwn ? $quotas[$siteId] : $defaultQuota;

        $rows[] = [
            'site_id'              => $siteId,
            'slug'                 => $site['slug'],
            'title'                => $site['title'],
            'owner_email'          => $site['owner_email'],
            'used_bytes'           => $used,
            'used_mb'              => bytesToMb($used),
            'diskquota_site_quota' => $quota,
            'quota_source'         => $hasOwn ? 'site' : 'default',
            'usage_percent'        => usagePercent($used, $quota),
        ];
    }

    return $rows;
}

/**
 * Run a two-column query and return it as a map of first column => second column.
 *
 * @param object $connection The Doctrine DBAL connection
 * @param string $sql        Query returning (id, value)
 * @return array Map of int id => value
 */
function fetchKeyValue($connection, $sql) {
    $map = [];
    foreach ($connection->fetchAllNumeric($sql) as $row) {
        $map[(int)$row[0]] = $row[1];
    }
    return $map;
}

/**
 * Read a user/site setting for every target that has it explicitly set.
 *
 * Omeka stores setting values JSON-encoded in the 'value' column.
 *
 * @param object $connection  The Doctrine DBAL connection
 * @param string $table       'user_setting' or 'site_setting'
 * @param string $targetColumn 'user_id' or 'site_id'
 * @param string $settingId   Setting name (e.g. 'diskquota_user_quota')
 * @return array Map of int target id => decoded value
 */
function fetchSettings($connection, $table, $targetColumn, $settingId) {
    $rows = $connection->fetchAllNumeric(
        "SELECT $targetColumn, value FROM $table WHERE id = ?",
        [$settingId]
    );

    $map = [];
    foreach ($rows as $row) {
        $map[(int)$row[0]] = json_decode($row[1], true);
    }
    return $map;
}

/**
 * Convert bytes to MB rounded to two decimals.
 *
 * @param int $bytes
 * @return float
 */
function bytesToMb($bytes) {
    return round($bytes / BYTES_PER_MB, 2);
}

/**
 * Percentage of the quota in use, or empty string when the quota is unlimited
 * (<= 0) or not numeric.
 *
 * @param int   $usedBytes
 * @param mixed $quotaMb
 * @return float|string
 */
function usagePercent($usedBytes, $quotaMb) {
    if (!is_numeric($quotaMb) || $quotaMb <= 0) {
        return '';
    }
    return round($usedBytes / ($quotaMb * BYTES_PER_MB) * 100, 2);
}

/**
 * Write rows to a CSV file with the given header.
 *
 * @param string $file   Output path
 * @param array  $header Column names (also the keys of each row)
 * @param array  $rows   List of associative arrays
 * @throws Exception If the file cannot be opened
 */
function writeCsv($file, $header, $rows) {
    $handle = fopen($file, 'w');
    if (!$handle) {
        throw new Exception("Could not open output file: $file");
    }

    fputcsv($handle, $header, ",", "\"", "\\");
    foreach ($rows as $row) {
        $line = [];
        foreach ($header as $column) {
            $line[] = $row[$column];
        }
        fputcsv($handle, $line, ",", "\"", "\\");
    }

    fclose($handle);
}
