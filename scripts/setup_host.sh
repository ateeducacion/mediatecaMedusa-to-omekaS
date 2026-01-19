#!/bin/bash
#
# Omeka-S Server Configuration Script for Migration
# This script prepares the Omeka-S server before starting the migration process
#
# Usage: sudo ./setup_host.sh [--proxy]
#
# Options:
#   --proxy    Enable proxy configuration for Medusa network
#

set -e

# Parse command line arguments
USE_PROXY=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --proxy)
            USE_PROXY=true
            shift
            ;;
        -h|--help)
            echo "Usage: sudo ./setup_host.sh [--proxy]"
            echo ""
            echo "Options:"
            echo "  --proxy    Enable proxy configuration for Medusa network"
            echo "  -h, --help Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Proxy configuration
PROXY_HTTP="http://proxydmz.medusa.gobiernodecanarias.net:3128/"
PROXY_HTTPS="http://proxydmz.medusa.gobiernodecanarias.net:3128/"
PROXY_NO_PROXY=".medusa.gobiernodecanarias.net,videoseducacion.gobiernodecanarias.org,.gobiernodecanarias.org"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base paths
OMEKA_PATH="/var/www/html"
BULKIMPORT_PATH="${OMEKA_PATH}/modules/BulkImport/data/mapping"
IMAGEMAGICK_POLICY="/etc/ImageMagick-7/policy.xml"

echo "=============================================="
echo "Omeka-S Server Configuration for Migration"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
    exit 1
fi

# Configure proxy if requested
if [ "$USE_PROXY" = true ]; then
    echo -e "${GREEN}Proxy configuration enabled${NC}"
    export HTTP_PROXY="$PROXY_HTTP"
    export HTTPS_PROXY="$PROXY_HTTPS"
    export NO_PROXY="$PROXY_NO_PROXY"
    export http_proxy="$PROXY_HTTP"
    export https_proxy="$PROXY_HTTPS"
    export no_proxy="$PROXY_NO_PROXY"
fi

# Function to check command success
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

# Function to download file with verification
download_file() {
    local url=$1
    local dest=$2
    local desc=$3

    echo -n "  Downloading ${desc}... "
    if curl -L -k -s -o "$dest" "$url"; then
        if [ -s "$dest" ]; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${RED}FAILED (empty file)${NC}"
            return 1
        fi
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

#------------------------------------------
# 1. Prepare directories and symbolic links
#------------------------------------------
echo "1. Creating symbolic links for migration..."

# bootstrap.php link (only if volume directory exists)
if [ -d "${OMEKA_PATH}/volume" ]; then
    if [ ! -L "${OMEKA_PATH}/volume/bootstrap.php" ]; then
        ln -sf "${OMEKA_PATH}/bootstrap.php" "${OMEKA_PATH}/volume/bootstrap.php"
        check_status "Created bootstrap.php symlink"
    else
        echo -e "${GREEN}✓ bootstrap.php symlink already exists${NC}"
    fi
else
    echo -e "${YELLOW}⚠ volume directory does not exist, skipping bootstrap.php symlink${NC}"
fi

# omeka-s link
if [ ! -L "${OMEKA_PATH}/omeka-s" ]; then
    ln -sf "${OMEKA_PATH}" "${OMEKA_PATH}/omeka-s"
    check_status "Created omeka-s symlink"
else
    echo -e "${GREEN}✓ omeka-s symlink already exists${NC}"
fi

# preload link for files/import (only if files/import directory exists)
if [ -d "${OMEKA_PATH}/files/import" ]; then
    if [ ! -L "${OMEKA_PATH}/files/preload" ]; then
        ln -sf "${OMEKA_PATH}/files/import" "${OMEKA_PATH}/files/preload"
        check_status "Created preload symlink"
    else
        echo -e "${GREEN}✓ preload symlink already exists${NC}"
    fi
else
    echo -e "${RED}✗ ERROR: ${OMEKA_PATH}/files/import directory does not exist${NC}"
    echo -e "${RED}  This directory is required for the migration. Please ensure Omeka-S is properly installed.${NC}"
    exit 1
fi
echo ""

#------------------------------------------
# 2. Check for ffmpeg installation
#------------------------------------------
echo "2. Checking ffmpeg installation..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1)
    echo -e "${GREEN}✓ ffmpeg is installed: ${FFMPEG_VERSION}${NC}"
else
    echo -e "${YELLOW}⚠ WARNING: ffmpeg is NOT installed!${NC}"
    echo -e "${YELLOW}  ffmpeg is required for video thumbnail generation.${NC}"
    echo -e "${YELLOW}  Please install it with: apt-get install ffmpeg (Debian/Ubuntu)${NC}"
    echo -e "${YELLOW}                       or: yum install ffmpeg (CentOS/RHEL)${NC}"
    echo ""
fi
echo ""

#------------------------------------------
# 3. Create directories for BulkImport XSL files
#------------------------------------------
echo "3. Setting up BulkImport XSL mapping files..."
mkdir -p "${BULKIMPORT_PATH}/xsl"
check_status "Created XSL directory"

download_file \
    "https://raw.githubusercontent.com/ateeducacion/migracion_mediateca/main/xsl/wp_omeka_itemset.xsl" \
    "${BULKIMPORT_PATH}/xsl/wp_omeka_itemset.xsl" \
    "wp_omeka_itemset.xsl"

download_file \
    "https://raw.githubusercontent.com/ateeducacion/migracion_mediateca/main/xsl/wp_omeka_items_preprocesor.xsl" \
    "${BULKIMPORT_PATH}/xsl/wp_omeka_items_preprocesor.xsl" \
    "wp_omeka_items_preprocesor.xsl"
echo ""

#------------------------------------------
# 4. Create directories for BulkImport XML mapper files
#------------------------------------------
echo "4. Setting up BulkImport XML mapping files..."
mkdir -p "${BULKIMPORT_PATH}/xml"
check_status "Created XML directory"

download_file \
    "https://raw.githubusercontent.com/ateeducacion/migracion_mediateca/main/Mapping/mapper_wp_xml_itemsets.xml" \
    "${BULKIMPORT_PATH}/xml/mapper_wp_xml_itemsets.xml" \
    "mapper_wp_xml_itemsets.xml"

download_file \
    "https://raw.githubusercontent.com/ateeducacion/migracion_mediateca/main/Mapping/mapper_wp_post_omeka_media.xml" \
    "${BULKIMPORT_PATH}/xml/mapper_wp_post_omeka_media.xml" \
    "mapper_wp_post_omeka_media.xml"

download_file \
    "https://raw.githubusercontent.com/ateeducacion/migracion_mediateca/main/Mapping/mapper_wp_post_omeka_items.xml" \
    "${BULKIMPORT_PATH}/xml/mapper_wp_post_omeka_items.xml" \
    "mapper_wp_post_omeka_items.xml"
echo ""

#------------------------------------------
# 5. Download migration scripts
#------------------------------------------
echo "5. Downloading migration scripts..."
mkdir -p "${OMEKA_PATH}/scripts"
check_status "Created scripts directory"

download_file \
    "https://github.com/ateeducacion/mediatecaMedusa-to-omekaS/raw/refs/heads/main/scripts/run_migration_tasks.php" \
    "${OMEKA_PATH}/scripts/run_migration_tasks.php" \
    "run_migration_tasks.php"

download_file \
    "https://github.com/ateeducacion/mediatecaMedusa-to-omekaS/raw/refs/heads/main/scripts/default_site_conf.json" \
    "${OMEKA_PATH}/scripts/default_site_conf.json" \
    "default_site_conf.json"
echo ""

#------------------------------------------
# 6. Configure ImageMagick policies
#------------------------------------------
echo "6. Configuring ImageMagick policies..."

if [ -f "$IMAGEMAGICK_POLICY" ]; then
    # Backup original policy file
    if [ ! -f "${IMAGEMAGICK_POLICY}.bak" ]; then
        cp "$IMAGEMAGICK_POLICY" "${IMAGEMAGICK_POLICY}.bak"
        echo -e "${GREEN}✓ Created backup of policy.xml${NC}"
    fi

    # Remove any existing policies for EPS, MP4, MOV before adding new ones
    sed -i '/pattern="EPS"/d' "$IMAGEMAGICK_POLICY"
    sed -i '/pattern="MP4"/d' "$IMAGEMAGICK_POLICY"
    sed -i '/pattern="MOV"/d' "$IMAGEMAGICK_POLICY"
    check_status "Removed existing EPS/MP4/MOV policies"

    # Add the new policies
    sed -i 's|</policymap>|  <policy domain="coder" rights="read" pattern="EPS"/>\n</policymap>|' "$IMAGEMAGICK_POLICY"
    sed -i 's|</policymap>|  <policy domain="coder" rights="read" pattern="MP4"/>\n</policymap>|' "$IMAGEMAGICK_POLICY"
    sed -i 's|</policymap>|  <policy domain="coder" rights="read" pattern="MOV"/>\n</policymap>|' "$IMAGEMAGICK_POLICY"
    check_status "Added new ImageMagick policies for EPS, MP4, MOV"
else
    echo -e "${YELLOW}⚠ WARNING: ImageMagick policy file not found at ${IMAGEMAGICK_POLICY}${NC}"
    echo -e "${YELLOW}  Please configure ImageMagick manually if needed.${NC}"
fi
echo ""

#------------------------------------------
# 7. Set proper permissions
#------------------------------------------
echo "7. Setting file permissions..."
chown -R www-data:www-data "${OMEKA_PATH}/scripts" 2>/dev/null || true
chown -R www-data:www-data "${BULKIMPORT_PATH}" 2>/dev/null || true
chmod -R 755 "${OMEKA_PATH}/scripts" 2>/dev/null || true
check_status "Set file permissions"
echo ""

#------------------------------------------
# Summary
#------------------------------------------
echo "=============================================="
echo -e "${GREEN}Server configuration completed!${NC}"
echo "=============================================="
echo ""
echo "Files installed:"
echo "  - ${BULKIMPORT_PATH}/xsl/wp_omeka_itemset.xsl"
echo "  - ${BULKIMPORT_PATH}/xsl/wp_omeka_items_preprocesor.xsl"
echo "  - ${BULKIMPORT_PATH}/xml/mapper_wp_xml_itemsets.xml"
echo "  - ${BULKIMPORT_PATH}/xml/mapper_wp_post_omeka_media.xml"
echo "  - ${BULKIMPORT_PATH}/xml/mapper_wp_post_omeka_items.xml"
echo "  - ${OMEKA_PATH}/scripts/run_migration_tasks.php"
echo "  - ${OMEKA_PATH}/scripts/default_site_conf.json"
echo ""
echo "Symbolic links created:"
echo "  - ${OMEKA_PATH}/volume/bootstrap.php -> ${OMEKA_PATH}/bootstrap.php"
echo "  - ${OMEKA_PATH}/omeka-s -> ${OMEKA_PATH}"
echo "  - ${OMEKA_PATH}/files/preload -> ${OMEKA_PATH}/files/import"
echo ""

if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠ Remember to install ffmpeg for video processing!${NC}"
    echo ""
fi

if [ "$USE_PROXY" = true ]; then
    echo "Proxy configuration was enabled for this session:"
    echo "  HTTP_PROXY=$PROXY_HTTP"
    echo "  HTTPS_PROXY=$PROXY_HTTPS"
    echo "  NO_PROXY=$PROXY_NO_PROXY"
    echo ""
fi

echo "The server is now ready for migration."
