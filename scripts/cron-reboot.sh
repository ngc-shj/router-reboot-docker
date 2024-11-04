#!/bin/bash

# Error handling
set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Log file
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/router-reboot.log"

# Timestamp for log
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

echo "$(timestamp) Starting router reboot process..." >> "${LOG_FILE}"

# Cleanup any existing container
if docker ps -a --format '{{.Names}}' | grep -q "^router-reboot$"; then
    echo "$(timestamp) Removing existing container..." >> "${LOG_FILE}"
    docker rm -f router-reboot >> "${LOG_FILE}" 2>&1
fi

# Run container
echo "$(timestamp) Starting new container..." >> "${LOG_FILE}"
docker run --rm \
    --name router-reboot \
    --network host \
    --shm-size=2g \
    -v "${PROJECT_ROOT}/config:/app/config" \
    router-reboot-docker >> "${LOG_FILE}" 2>&1

echo "$(timestamp) Router reboot process completed" >> "${LOG_FILE}"

