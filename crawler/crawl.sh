#!/bin/bash

# This script is designed to run the Elastic Crawler in a Docker container.
# It requires a configuration file to specify the crawler's behavior.

# Displays the script's usage instructions and then exits.
usage() {
    echo ""
    echo "Usage: $0 -c <config_file>"
    echo ""
    echo "  -c <config_file> : Path to the crawler configuration YAML file."
    echo "  -o <output_directory> : Path to the directory where crawler output will be saved."
    echo "                          Defaults to './output' if not specified."
    echo ""
    echo "Example: $0 -c crawler.yml"
    echo ""
    exit 1
}

# -------------
# Main Script
# -------------

# Initialize variables
CONFIG_FILE=""        # Stores the path to the crawler configuration file.
OUTPUT_DIR="./output" # Stores the path to the output directory.

# Parse command-line options using getopts.
# 'h' is for displaying help (no argument).
# 'c:' is for the configuration file (requires an argument).
# 'o:' is for the output directory (requires an argument).
while getopts "hc:o:" opt; do
    case ${opt} in
        h)
            usage
            ;;
        c)
            CONFIG_FILE="$OPTARG"
            echo "Configuration file specified : ${CONFIG_FILE}"
            ;;
        o)
            OUTPUT_DIR="$OPTARG"
            echo "Output directory specified   : ${OUTPUT_DIR}"
            ;;
        \?) # Handles invalid options.
            echo "Error: Invalid option -${OPTARG}." >&2
            usage
            ;;
    esac
done
shift $((OPTIND - 1))


# Input Validation

# Check if the configuration file path was provided.
if [[ -z "${CONFIG_FILE}" ]]; then
    echo "ERROR: Missing parameter: -c (configuration file path is required)." >&2
    usage
fi

# Check if the provided configuration file actually exists.
if [[ ! -f "${CONFIG_FILE}" ]]; then
    echo "ERROR: Configuration file '${CONFIG_FILE}' not found." >&2
    usage
fi

# --- Prepare Output Directory ---
mkdir -p "${OUTPUT_DIR}" || { echo "ERROR: Could not create output directory '${OUTPUT_DIR}'. Aborting." >&2; exit 1; }

# --- Docker Command Execution ---
CONFIG_FILENAME=$(basename "${CONFIG_FILE}")
CONFIG_FILE_DIR=$(dirname "${CONFIG_FILE}")
ABS_CONFIG_FILE_DIR=$(cd "${CONFIG_FILE_DIR}" && pwd -P) || { echo "ERROR: Could not resolve absolute path for config file directory." >&2; exit 1; }
ABS_OUTPUT_DIR=$(cd "${OUTPUT_DIR}" && pwd -P) || { echo "ERROR: Could not resolve absolute path for output directory." >&2; exit 1; }
CURRENT_HOST_UID=$(id -u)
CURRENT_HOST_GID=$(id -g)

echo -e "Starting Elastic Crawler in Docker container...\n"
docker run \
    --user "${CURRENT_HOST_UID}:${CURRENT_HOST_GID}" \
    -v "${ABS_CONFIG_FILE_DIR}":/config \
    -v "${ABS_OUTPUT_DIR}":/output \
    -it \
    docker.elastic.co/integrations/crawler:latest \
    jruby bin/crawler crawl "/config/${CONFIG_FILENAME}"

# --- Post-Execution ---
echo "Crawl terminated. Check the '${OUTPUT_DIR}' directory for crawler results."