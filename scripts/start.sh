#!/bin/bash
# scripts/start.sh — Run this once to set up the project from scratch

set -e

echo "=== ABBK Platform Setup ==="

# 1. Copy env file
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env — fill in your API keys before continuing"
  exit 1
fi

# 2. Build all containers
docker compose build

# 3. Start database and redis first
docker compose up -d db redis
echo "Waiting for database to be ready..."
sleep 5

# 4. Run database migrations
docker compose run --rm backend alembic upgrade head

# 5. Start all remaining services
docker compose up -d

echo ""
echo "=== All services running ==="
echo "  Frontend:  http://localhost:5173"
echo "  API:       http://localhost:8000"
echo "  API docs:  http://localhost:8000/docs"
echo "  Flower:    http://localhost:5555"
echo ""
echo "Tip: watch logs with: docker compose logs -f"
