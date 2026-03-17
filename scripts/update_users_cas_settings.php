#!/usr/bin/env php
<?php
/**
 * Update Users CAS Settings Script
 *
 * This script configures Omeka S users to properly access the admin panel using CAS:
 *   1. Adds a record in the `cas_user` table with (user_name, user_id) so that the CAS
 *      identity is linked to the Omeka user (the Omeka username is assumed to match the CAS username).
 *   2. Sets the user setting `default_resource_template` to the value passed via
 *      --resource-template-id.
 *
 * Usage:
 *   php update_users_cas_settings.php --resource-template-id <id> [--user-id <id>] [--omeka-path <path>]
 *
 * Arguments:
 *   --resource-template-id   ID of the resource template to set as default (required)
 *   --user-id                Only process this user ID. If omitted, all users are processed
 *                            (requires typing 'CHANGE ALL' to confirm).
 *   --omeka-path             Path to the Omeka S installation (default: /var/www/html)
 *
 * Author: ATE - Área de Tecnología Educativa
 * Date: 2026-03-17
 */

// Define constants
define('SCRIPT_VERSION', '1.0.0');

// Parse command line arguments
$options = getopt('', ['resource-template-id:', 'user-id::', 'omeka-path::']);

// Validate required arguments
if (!isset($options['resource-template-id'])) {
    echo "Error: Missing required argument --resource-template-id.\n";
    echo "Usage: php update_users_cas_settings.php --resource-template-id <id> [--user-id <id>] [--omeka-path <path>]\n";
    exit(1);
}

$resourceTemplateId = (int)$options['resource-template-id'];
$targetUserId       = isset($options['user-id']) ? (int)$options['user-id'] : null;
$omekaPath          = isset($options['omeka-path']) ? $options['omeka-path'] : '/var/www/html';

// Display script info
echo "===========================================\n";
echo "Update Users CAS Settings Script\n";
echo "Version: " . SCRIPT_VERSION . "\n";
echo "===========================================\n";
echo "Resource template ID : $resourceTemplateId\n";
echo "Target user ID       : " . ($targetUserId ? $targetUserId : 'ALL') . "\n";
echo "Omeka path           : $omekaPath\n";
echo "-------------------------------------------\n";

// If no --user-id is given, ask for explicit confirmation before touching all users
if ($targetUserId === null) {
    echo "\n========================================\n";
    echo "WARNING: You are about to update ALL users!\n";
    echo "========================================\n";
    echo "Type 'CHANGE ALL' to confirm (case sensitive): ";

    $handle       = fopen("php://stdin", "r");
    $confirmation = trim(fgets($handle));
    fclose($handle);

    if ($confirmation !== 'CHANGE ALL') {
        echo "Operation cancelled. Confirmation not received.\n";
        exit(0);
    }

    echo "Confirmation received. Proceeding with all users...\n\n";
}

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

echo "-------------------------------------------\n";

// Validate that the resource template exists
echo "Validating resource template ID $resourceTemplateId...\n";
try {
    $api->read('resource_templates', $resourceTemplateId);
    echo "Resource template ID $resourceTemplateId found.\n";
} catch (Exception $e) {
    echo "Error: Resource template ID $resourceTemplateId not found: " . $e->getMessage() . "\n";
    exit(1);
}

echo "-------------------------------------------\n";

// Build the list of users to process
if ($targetUserId !== null) {
    $userEntity = $entityManager->find('Omeka\Entity\User', $targetUserId);
    if (!$userEntity) {
        echo "Error: User with ID $targetUserId not found.\n";
        exit(1);
    }
    $users = [$userEntity];
} else {
    echo "Retrieving all users from database...\n";
    $users = $entityManager->getRepository('Omeka\Entity\User')->findAll();
    echo "Found " . count($users) . " user(s) to process.\n";
}

echo "-------------------------------------------\n";

// Get the raw database connection for direct inserts/updates on cas_user
$connection = $serviceLocator->get('Omeka\Connection');

// Get the UserSettings service
$userSettings = $serviceLocator->get('Omeka\Settings\User');

// Process users
$totalUsers   = count($users);
$successCount = 0;
$failureCount = 0;

foreach ($users as $index => $userEntity) {
    $userId   = $userEntity->getId();
    $userName = $userEntity->getName();
    $userNum  = $index + 1;

    echo "\n[$userNum/$totalUsers] Processing user ID: $userId (name: $userName)\n";

    $userSuccess = true;

    // --- Step 1: Register user in cas_user table ---
    $userSuccess = addCasUser($userId, $userName, $connection) && $userSuccess;

    // --- Step 2: Set default_resource_template user setting ---
    $userSuccess = setDefaultResourceTemplate($userId, $resourceTemplateId, $userSettings, $entityManager) && $userSuccess;

    if ($userSuccess) {
        echo "  ✓ User $userId updated successfully\n";
        $successCount++;
    } else {
        echo "  ✗ User $userId had one or more errors\n";
        $failureCount++;
    }
}

// Summary
echo "\n==========================================\n";
echo "SUMMARY\n";
echo "==========================================\n";
echo "Total users processed : $totalUsers\n";
echo "Successful            : $successCount\n";
echo "Failed                : $failureCount\n";
echo "\nScript completed.\n";

exit($failureCount > 0 ? 1 : 0);

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Insert or update a row in the cas_user table linking the CAS username to the
 * Omeka user ID. If the user already has an entry, the username is updated to
 * match the current Omeka username.
 *
 * @param int    $userId     The Omeka user ID
 * @param string $userName   The Omeka (and CAS) username
 * @param object $connection The Doctrine DBAL connection
 * @return bool True if successful, false otherwise
 */
function addCasUser($userId, $userName, $connection) {
    try {
        echo "  [CAS] Checking cas_user entry for user ID $userId (username: $userName)...\n";

        // Check whether a record already exists for this user_id
        $existing = $connection->fetchAssociative(
            'SELECT id, user_name FROM cas_user WHERE user_id = ?',
            [$userId]
        );

        if ($existing) {
            if ($existing['user_name'] === $userName) {
                echo "  [CAS] Entry already exists with correct username. No update needed.\n";
            } else {
                // Update the username to match current Omeka username
                $connection->executeStatement(
                    'UPDATE cas_user SET user_name = ? WHERE user_id = ?',
                    [$userName, $userId]
                );
                echo "  [CAS] Updated username from '{$existing['user_name']}' to '$userName'.\n";
            }
        } else {
            // Insert a new record
            $connection->executeStatement(
                'INSERT INTO cas_user (user_name, user_id) VALUES (?, ?)',
                [$userName, $userId]
            );
            echo "  [CAS] Created cas_user entry: user_name='$userName', user_id=$userId.\n";
        }

        return true;
    } catch (Exception $e) {
        echo "  [CAS] Error updating cas_user for user $userId: " . $e->getMessage() . "\n";
        return false;
    }
}

/**
 * Set the user setting 'default_resource_template' for a given user.
 *
 * @param int    $userId             The Omeka user ID
 * @param int    $resourceTemplateId The resource template ID to set as default
 * @param object $userSettings       The Omeka UserSettings service
 * @param object $entityManager      The Doctrine entity manager
 * @return bool True if successful, false otherwise
 */
function setDefaultResourceTemplate($userId, $resourceTemplateId, $userSettings, $entityManager) {
    try {
        echo "  [Settings] Setting default_resource_template=$resourceTemplateId for user $userId...\n";

        // Ensure the user entity exists before setting user settings
        $userEntity = $entityManager->find('Omeka\Entity\User', $userId);
        if (!$userEntity) {
            echo "  [Settings] Error: User entity not found for ID $userId.\n";
            return false;
        }

        // Target the user in the UserSettings service
        $userSettings->setTargetId($userId);

        // Set the default resource template
        $userSettings->set('default_resource_template', $resourceTemplateId);

        echo "  [Settings] default_resource_template set to $resourceTemplateId.\n";
        return true;
    } catch (Exception $e) {
        echo "  [Settings] Error setting default_resource_template for user $userId: " . $e->getMessage() . "\n";
        return false;
    }
}
