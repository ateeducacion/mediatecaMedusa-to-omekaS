#!/bin/zsh
#
# setup_venv.sh
#
# SYNOPSIS
#   Sets up the Python virtual environment for the mediateca-to-omeka project.
#
# DESCRIPTION
#   Ensures Python 3.8+, creates or reuses the project virtual environment, upgrades pip, and installs
#   the project in editable mode. All actions are logged to the logs directory.
#
# USAGE
#   chmod +x setup_venv.sh
#   ./setup_venv.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="${0:A:h}"
PROJECT_ROOT="${SCRIPT_DIR}"

# Change to project root
cd "${PROJECT_ROOT}"
echo "HOLA"
# Initialize variables
LOG_FILE=""
EXIT_CODE=0

# Cleanup function
cleanup() {
    if [[ -n "${LOG_FILE}" ]]; then
        echo "Log saved to: ${LOG_FILE}"
    fi
    exit ${EXIT_CODE}
}

trap cleanup EXIT

# Logging function that writes to both stdout and log file
log() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
    if [[ -n "${LOG_FILE}" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${message}" >> "${LOG_FILE}"
    fi
}

# Create logs directory
LOG_DIR="${PROJECT_ROOT}/logs"
if [[ ! -d "${LOG_DIR}" ]]; then
    echo -e "${CYAN}Creating log directory at ${LOG_DIR}${NC}"
    mkdir -p "${LOG_DIR}"
fi

# Create log file
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="${LOG_DIR}/setup_${TIMESTAMP}.log"
touch "${LOG_FILE}"

log "${CYAN}" "Starting virtual environment setup for mediateca-to-omeka."

# Check for Python
if ! command -v python3 &> /dev/null; then
    log "${RED}" "Python executable not found. Install Python 3.8 or newer and rerun the script."
    EXIT_CODE=1
    exit 1
fi

PYTHON_CMD=$(command -v python3)

# Check Python version
PYTHON_VERSION_OUTPUT=$(${PYTHON_CMD} --version 2>&1)
PYTHON_VERSION=$(echo "${PYTHON_VERSION_OUTPUT}" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

if [[ -z "${PYTHON_VERSION}" ]]; then
    log "${RED}" "Unable to determine Python version from output: ${PYTHON_VERSION_OUTPUT}"
    EXIT_CODE=1
    exit 1
fi

# Extract major and minor version
MAJOR_VERSION=$(echo "${PYTHON_VERSION}" | cut -d. -f1)
MINOR_VERSION=$(echo "${PYTHON_VERSION}" | cut -d. -f2)

if [[ ${MAJOR_VERSION} -lt 3 ]] || [[ ${MAJOR_VERSION} -eq 3 && ${MINOR_VERSION} -lt 8 ]]; then
    log "${RED}" "Detected Python version ${PYTHON_VERSION}. Python 3.8 or newer is required."
    EXIT_CODE=1
    exit 1
fi

log "${GREEN}" "Python ${PYTHON_VERSION} detected at ${PYTHON_CMD}."

# Create or reuse virtual environment
VENV_PATH="${PROJECT_ROOT}/venv"
if [[ ! -d "${VENV_PATH}" ]]; then
    log "${CYAN}" "Creating virtual environment at ${VENV_PATH}"
    ${PYTHON_CMD} -m venv "${VENV_PATH}"
else
    log "${YELLOW}" "Virtual environment already present at ${VENV_PATH}"
fi

# Check for activation script
ACTIVATE_SCRIPT="${VENV_PATH}/bin/activate"
if [[ ! -f "${ACTIVATE_SCRIPT}" ]]; then
    log "${RED}" "Activation script not found at ${ACTIVATE_SCRIPT}. The virtual environment may be incomplete."
    EXIT_CODE=1
    exit 1
fi

# Activate virtual environment
log "${CYAN}" "Activating virtual environment."
source "${ACTIVATE_SCRIPT}"

# Upgrade pip and install project
{
    log "${CYAN}" "Upgrading pip in the virtual environment."
    python -m pip install --upgrade pip

    log "${CYAN}" "Installing project in editable mode (pip install -e .)."
    pip install -e .
} || {
    log "${RED}" "Failed to install dependencies."
    EXIT_CODE=1
}

# Deactivate virtual environment
if command -v deactivate &> /dev/null; then
    log "${CYAN}" "Deactivating virtual environment."
    deactivate
fi

if [[ ${EXIT_CODE} -eq 0 ]]; then
    log "${GREEN}" "Virtual environment setup completed successfully."
    log "${GREEN}" "Activate it manually when needed with:"
    log "${GREEN}" "    source ./venv/bin/activate"
else
    log "${RED}" "Environment setup failed."
fi
