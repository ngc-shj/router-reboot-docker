#!/bin/bash

# エラーが発生したら即座に終了
set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# バージョン情報を取得（Git tagから）
VERSION=$(git describe --tags --always --dirty)
if [ -z "$VERSION" ]; then
    VERSION="dev"
fi

echo "Building router-reboot-docker version: $VERSION"

# イメージ名を設定
IMAGE_NAME="router-reboot-docker"
FULL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"

# Dockerイメージをビルド
echo "Building Docker image..."
docker build -t ${FULL_IMAGE_NAME} \
    --build-arg VERSION=${VERSION} \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VCS_REF=$(git rev-parse --short HEAD) \
    ${SCRIPT_DIR}

# latestタグも作成
docker tag ${FULL_IMAGE_NAME} ${IMAGE_NAME}:latest

echo "Build completed successfully!"
echo "Image: ${FULL_IMAGE_NAME}"
echo "Latest tag: ${IMAGE_NAME}:latest"

