#!/usr/bin/env php
<?php
/**
 * Set Primary Thumbnail Media Script
 *
 * This script updates the primary media of items to use a media with 'thumb' in the source field.
 * For each item, it finds the first media with source LIKE 'thumb%' and sets it as the primary media.
 *
 * Usage:
 *   php set_primary_thumbnail_media.php [--site-id <site_id>] [--omeka-path <path>]
 *
 * Arguments:
 *   --site-id        (Optional) Process only items from this site ID. If not provided, processes all items from all sites
 *   --omeka-path     Path to the Omeka S installation (default: /var/www/html)
 *
 * Author: ATE
 * Date: 2026-02-13
 */

// Define constants
define('SCRIPT_VERSION', '1.0.0');

// Parse command line arguments
$options = getopt('', ['site-id::', 'omeka-path::']);

// Get parameters
$siteId = isset($options['site-id']) ? (int)$options['site-id'] : null;
$omekaPath = isset($options['omeka-path']) ? $options['omeka-path'] : '/var/www/html';

// Display script info
echo "===========================================\n";
echo "Set Primary Thumbnail Media Script\n";
echo "Version: " . SCRIPT_VERSION . "\n";
echo "===========================================\n";

if ($siteId) {
    echo "Processing items from site ID: $siteId\n";
} else {
    echo "Processing items from ALL sites\n";
}
echo "Omeka path: $omekaPath\n";
echo "-------------------------------------------\n";

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

echo "-------------------------------------------\n";

// Step 1: Find all media with 'thumb' in source using DQL
echo "Step 1: Finding all media with 'thumb' in source...\n";

$dql = "SELECT m.id as media_id, m.source, i.id as item_id
        FROM Omeka\Entity\Media m
        JOIN m.item i ";

// Add site filter if specified
if ($siteId) {
    $dql .= "JOIN i.sites s WHERE s.id = :siteId AND ";
} else {
    $dql .= "WHERE ";
}

$dql .= "m.source LIKE :thumbPattern
         ORDER BY i.id, m.position";

$query = $entityManager->createQuery($dql);
$query->setParameter('thumbPattern', '%thumb%');
if ($siteId) {
    $query->setParameter('siteId', $siteId);
}

$results = $query->getResult();

if (empty($results)) {
    echo "No media with 'thumb' in source found.\n";
    echo "===========================================\n";
    exit(0);
}

echo "Found " . count($results) . " media with 'thumb' in source\n";

// Step 2: Group media by item_id and get the first media for each item
echo "Step 2: Grouping media by item...\n";

$itemMediaMap = [];
foreach ($results as $result) {
    $itemId = $result['item_id'];
    $mediaId = $result['media_id'];

    // Only store the first media found for each item
    if (!isset($itemMediaMap[$itemId])) {
        $itemMediaMap[$itemId] = $mediaId;
    }
}

$totalItems = count($itemMediaMap);
echo "Found $totalItems unique items with thumbnail media\n";
echo "-------------------------------------------\n";

// Step 3: Process each item
echo "Step 3: Processing items...\n";

// Statistics
$processedCount = 0;
$updatedCount = 0;
$skippedCount = 0;
$errorCount = 0;

foreach ($itemMediaMap as $itemId => $thumbnailMediaId) {
    $processedCount++;

    try {
        // Get the item
        $item = $api->read('items', $itemId)->getContent();

        // Get current primary media
        $currentPrimaryMedia = $item->primaryMedia();

        // Check if the thumbnail media is already the primary media
        if ($currentPrimaryMedia && $currentPrimaryMedia->id() === $thumbnailMediaId) {
            echo "[$processedCount/$totalItems] Item ID $itemId: Thumbnail media (ID $thumbnailMediaId) is already primary, skipping\n";
            $skippedCount++;
            continue;
        }

        // Update the item to set the thumbnail media as primary
        $updateData = [
            'o:primary_media' => ['o:id' => $thumbnailMediaId]
        ];

        $api->update('items', $itemId, $updateData, [], ['isPartial' => true]);

        echo "[$processedCount/$totalItems] Item ID $itemId: Updated primary media to thumbnail (Media ID $thumbnailMediaId)\n";
        $updatedCount++;

        // Clear entity manager periodically to prevent memory issues
        if ($processedCount % 100 === 0) {
            $entityManager->clear();
        }

    } catch (Exception $e) {
        echo "[$processedCount/$totalItems] Item ID $itemId: ERROR - " . $e->getMessage() . "\n";
        $errorCount++;
    }
}

// Display final statistics
echo "===========================================\n";
echo "Process completed!\n";
echo "-------------------------------------------\n";
echo "Total items processed: $processedCount\n";
echo "Items updated: $updatedCount\n";
echo "Items skipped: $skippedCount\n";
echo "Errors: $errorCount\n";
echo "===========================================\n";

exit(0);
