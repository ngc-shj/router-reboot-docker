#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the project root directory
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Get version information from Git tags
VERSION=$(git describe --tags --always --dirty)
if [ -z "$VERSION" ]; then
    VERSION="dev"
fi

echo "Building router-reboot-docker version: $VERSION"

# Set image name
IMAGE_NAME="router-reboot-docker"
FULL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"

# Build Docker image
echo "Building Docker image..."
docker build -t ${FULL_IMAGE_NAME} \
    --build-arg VERSION=${VERSION} \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VCS_REF=$(git rev-parse --short HEAD) \
    ${PROJECT_ROOT}

# Create latest tag
docker tag ${FULL_IMAGE_NAME} ${IMAGE_NAME}:latest

echo "Build completed successfully!"
echo "Image: ${FULL_IMAGE_NAME}"
echo "Latest tag: ${IMAGE_NAME}:latest"

