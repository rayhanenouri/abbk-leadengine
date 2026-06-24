FROM python:3.12-slim

# Install system dependencies (Playwright needs these)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN pip install uv

WORKDIR /app

# Copy dependency files first (layer caching — only reinstalls if changed)
COPY pyproject.toml .
COPY uv.lock* .

# Install Python dependencies
RUN uv pip install --system -r pyproject.toml

# Install Playwright browsers + system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers (Chromium only for headless scraping)
RUN playwright install chromium

# Copy source code
COPY . .

EXPOSE 8000
