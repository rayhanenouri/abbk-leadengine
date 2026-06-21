#!/bin/bash
# Simple test for training spider - verify it's working

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  ABBK LeadEngine — Training Spider Verification"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Step 1: Checking if spider exists..."
if docker compose exec -T worker python -c "from app.scrapers.spiders.training_spider import TrainingCentersSpider; print('✓ Spider imported successfully')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Training spider code is valid"
else
    echo "✗ Spider import failed - check syntax errors"
    exit 1
fi

echo ""
echo "Step 2: Checking Celery task registration..."
if docker compose exec -T worker celery -A app.workers.celery_app inspect registered | grep -q "scrape_training"; then
    echo -e "${GREEN}✓${NC} Training scraper task is registered"
else
    echo "⚠ Training task not found in registered tasks"
fi

echo ""
echo "Step 3: Triggering manual test run..."
echo "Note: This will attempt to scrape ISET and training center websites"
echo ""

# Trigger the Celery task
docker compose exec -T worker celery -A app.workers.celery_app call app.workers.tasks.scraping.scrape_training &
TASK_PID=$!

echo "Task queued! PID: $TASK_PID"
echo ""
echo "Monitor progress with:"
echo "  docker compose logs -f worker"
echo ""
echo "Check results in database:"
echo "  SELECT COUNT(*) FROM lead_signals WHERE signal_type = 'training_detected';"
echo ""
echo "════════════════════════════════════════════════════════════════"
