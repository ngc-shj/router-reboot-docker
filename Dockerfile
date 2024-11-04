FROM python:3.9-slim

# システムパッケージをインストール
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# タイムゾーンを設定
ENV TZ=Asia/Tokyo

# Python依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Chrome関連のディレクトリを設定
RUN mkdir -p /tmp/chrome && \
    mkdir -p /selenium-cache

# 環境変数を設定
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DISPLAY=:99 \
    SELENIUM_CACHE_DIR=/selenium-cache

# 実行ユーザーを作成
RUN useradd -r -s /bin/false appuser

# エントリーポイントスクリプトを作成
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &\nexec python reboot.py' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# アプリケーションディレクトリ構造を作成
RUN mkdir -p /app/config && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chown -R appuser:appuser /tmp/chrome && \
    chmod -R 777 /tmp/chrome && \
    chown -R appuser:appuser /selenium-cache && \
    chmod -R 777 /selenium-cache

# スクリプトをコピー
COPY src/reboot.py .

# 設定ファイルは外部からマウント
VOLUME /app/config

# 実行ユーザーに切り替え
USER appuser

# エントリーポイントを設定
ENTRYPOINT ["/app/entrypoint.sh"]
