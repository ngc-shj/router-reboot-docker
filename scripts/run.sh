#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the project root directory
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Default settings
IMAGE_NAME="router-reboot-docker"
CONFIG_DIR="${PROJECT_ROOT}/config"
CONTAINER_NAME="router-reboot"

# Help function to display usage
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -c, --config <dir>   Specify config directory (default: ./config)"
    echo "  -t, --tag <tag>      Specify image tag (default: latest)"
    echo "  -n, --name <name>    Specify container name (default: router-reboot)"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--config)
            CONFIG_DIR="$2"
            shift
            shift
            ;;
        -t|--tag)
            TAG="$2"
            shift
            shift
            ;;
        -n|--name)
            CONTAINER_NAME="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if config directory exists, create if not
if [ ! -d "$CONFIG_DIR" ]; then
    echo "Config directory not found: $CONFIG_DIR"
    echo "Creating config directory..."
    mkdir -p "$CONFIG_DIR"
    
    # Create default configuration file
    echo "Creating example configuration..."
    cat > "${CONFIG_DIR}/config.yml" << EOF
router:
  connection:
    base_url: "http://192.168.11.1"
    timeout_seconds: 30
  
  auth:
    username: "admin"
    password: ""
    
  endpoints:
    login: "login.html"
    reboot: "save_init.html"
  
  options:
    verify_ssl: false
    retry_count: 3
    retry_interval_seconds: 5
    mobile_mode: false
EOF
    echo "Example configuration created"
fi

# Stop and remove existing container if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping and removing existing container..."
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
fi

# Start the container
echo "Starting router-reboot container..."
docker run -d \
    --name ${CONTAINER_NAME} \
    --network host \
    -v "${CONFIG_DIR}:/app/config" \
    -e TZ=Asia/Tokyo \
    ${IMAGE_NAME}:${TAG:-latest}

# Display success message and useful information
echo "Container started successfully!"
echo "Container name: ${CONTAINER_NAME}"
echo "Config directory: ${CONFIG_DIR}"
echo "Logs: docker logs ${CONTAINER_NAME}"

