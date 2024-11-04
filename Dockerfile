FROM python:3.9-slim

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# タイムゾーンを設定
ENV TZ=Asia/Tokyo

# Python依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションディレクトリ構造を作成
RUN mkdir -p /app/config

# スクリプトをコピー
COPY src/reboot.py .

# 設定ファイルは外部からマウント
VOLUME /app/config

# 実行ユーザーを作成
RUN useradd -r -s /bin/false appuser && \
    chown -R appuser:appuser /app

# Chrome関連の環境変数を設定
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DISPLAY=:99

USER appuser

# エントリーポイントスクリプトを実行
CMD ["python", "reboot.py"]

