FROM python:3.9-slim

# Install system packages
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Set timezone
ENV TZ=Asia/Tokyo

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -r -s /bin/false appuser

# Create necessary directories and set permissions
RUN mkdir -p /tmp/chrome && \
    mkdir -p /app/config && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /tmp/chrome && \
    chmod -R 755 /app && \
    chmod -R 777 /tmp/chrome

# Set environment variables
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    PYTHONUNBUFFERED=1

# Copy source code and set ownership
COPY src/reboot.py .
RUN chown appuser:appuser /app/reboot.py

# Mount config volume
VOLUME /app/config

# Switch to non-root user
USER appuser

# Start the script
CMD ["python", "reboot.py"]

