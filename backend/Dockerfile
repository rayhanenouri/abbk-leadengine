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

# Install Playwright browsers (for JS-heavy scraping)
# Skipping for now - install later if needed: playwright install chromium --with-deps
# RUN playwright install chromium --with-deps || true

# Copy source code
COPY . .

EXPOSE 8000
