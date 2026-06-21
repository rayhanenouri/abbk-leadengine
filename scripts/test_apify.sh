#!/bin/bash
# Test script for Apify LinkedIn integration

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  ABBK LeadEngine — Apify LinkedIn Integration Test"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if APIFY_API_TOKEN is set
echo "Step 1: Checking APIFY_API_TOKEN..."
if grep -q "APIFY_API_TOKEN=apify_api_" .env 2>/dev/null; then
    echo -e "${GREEN}✓${NC} APIFY_API_TOKEN is set in .env"
else
    echo -e "${RED}✗${NC} APIFY_API_TOKEN not set or invalid"
    echo ""
    echo "Please add your Apify API token to .env:"
    echo "  APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    echo ""
    echo "Get your token from: https://console.apify.com/account/integrations"
    exit 1
fi

echo ""

# Get JWT token
echo "Step 2: Getting JWT token..."
JWT_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@abbk.tn","password":"admin123"}' | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -z "$JWT_TOKEN" ]; then
    echo -e "${RED}✗${NC} Failed to get JWT token"
    echo "Make sure the API is running: docker compose ps"
    exit 1
fi

echo -e "${GREEN}✓${NC} JWT token obtained"
echo ""

# Get first lead with LinkedIn URL
echo "Step 3: Finding lead with LinkedIn URL..."
LEAD_DATA=$(curl -s "http://localhost:8000/api/leads?limit=100" \
    -H "Authorization: Bearer $JWT_TOKEN" | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
for lead in data.get('leads', []):
    if lead.get('linkedin_url'):
        print(json.dumps(lead))
        break
" 2>/dev/null || echo "")

if [ -z "$LEAD_DATA" ]; then
    echo -e "${YELLOW}⚠${NC} No leads with LinkedIn URL found"
    echo ""
    echo "Creating a test lead with LinkedIn URL..."

    # Create test lead
    LEAD_DATA=$(curl -s -X POST "http://localhost:8000/api/leads" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "company_name": "Poulina Group Holding",
            "website": "https://www.poulina.com.tn",
            "linkedin_url": "https://www.linkedin.com/company/poulina-group-holding",
            "country": "Tunisia",
            "city": "Tunis",
            "sector": "Diversified Conglomerate"
        }' 2>/dev/null || echo "")

    if [ -z "$LEAD_DATA" ]; then
        echo -e "${RED}✗${NC} Failed to create test lead"
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Test lead created"
fi

LEAD_ID=$(echo "$LEAD_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
LEAD_NAME=$(echo "$LEAD_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['company_name'])")
LEAD_LINKEDIN=$(echo "$LEAD_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin).get('linkedin_url', 'N/A'))")

echo -e "${GREEN}✓${NC} Found lead: $LEAD_NAME (ID: $LEAD_ID)"
echo "  LinkedIn: $LEAD_LINKEDIN"
echo ""

# Check if already enriched
echo "Step 4: Checking enrichment status..."
LINKEDIN_DATA=$(echo "$LEAD_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
linkedin = data.get('scraped_data', {}).get('linkedin')
if linkedin:
    print(json.dumps(linkedin, indent=2))
" 2>/dev/null || echo "")

if [ -n "$LINKEDIN_DATA" ]; then
    echo -e "${YELLOW}ℹ${NC} Lead already has LinkedIn data:"
    echo "$LINKEDIN_DATA" | head -20
    echo ""
    read -p "Enrich again? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping enrichment."
        exit 0
    fi
fi

# Trigger enrichment
echo "Step 5: Triggering LinkedIn enrichment..."
TASK_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/leads/$LEAD_ID/enrich-linkedin" \
    -H "Authorization: Bearer $JWT_TOKEN")

echo "$TASK_RESPONSE" | python3 -m json.tool
echo ""

TASK_ID=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('task_id', ''))" 2>/dev/null || echo "")

if [ -z "$TASK_ID" ]; then
    echo -e "${RED}✗${NC} Failed to trigger enrichment task"
    exit 1
fi

echo -e "${GREEN}✓${NC} Enrichment task queued: $TASK_ID"
echo ""

echo "Step 6: Monitoring task progress..."
echo "Note: Apify scraping can take 30-120 seconds per company"
echo ""

# Monitor worker logs
echo "Watching Celery worker logs (Ctrl+C to stop)..."
echo "════════════════════════════════════════════════════════════════"
docker compose logs -f worker --tail 50 &
LOGS_PID=$!

# Wait for task to complete (max 5 minutes)
for i in {1..60}; do
    sleep 5

    # Check if task completed
    UPDATED_LEAD=$(curl -s "http://localhost:8000/api/leads/$LEAD_ID" \
        -H "Authorization: Bearer $JWT_TOKEN")

    HAS_LINKEDIN=$(echo "$UPDATED_LEAD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
linkedin = data.get('scraped_data', {}).get('linkedin')
if linkedin and linkedin.get('employee_count'):
    print('yes')
" 2>/dev/null || echo "")

    if [ "$HAS_LINKEDIN" = "yes" ]; then
        kill $LOGS_PID 2>/dev/null || true
        echo ""
        echo -e "${GREEN}✓${NC} Enrichment completed!"
        echo ""

        # Show results
        echo "════════════════════════════════════════════════════════════════"
        echo "  ENRICHMENT RESULTS"
        echo "════════════════════════════════════════════════════════════════"
        echo "$UPDATED_LEAD" | python3 -c "
import sys, json
data = json.load(sys.stdin)
linkedin = data.get('scraped_data', {}).get('linkedin', {})

print(f\"Company: {data['company_name']}\")
print(f\"Employee Count: {linkedin.get('employee_count', 'N/A')}\")
print(f\"Industry: {linkedin.get('industry', 'N/A')}\")
print(f\"Description: {linkedin.get('description', 'N/A')[:100]}...\")
print(f\"Specialties: {', '.join(linkedin.get('specialties', []))}\")
print(f\"Employees scraped: {len(linkedin.get('employees', []))}\")
print()

# Show engineering roles
employees = linkedin.get('employees', [])
eng_keywords = ['ingénieur', 'engineer', 'conception', 'design', 'CAD', 'R&D', 'mécanique']
eng_roles = [emp for emp in employees if any(kw.lower() in emp.get('title', '').lower() for kw in eng_keywords)]

if eng_roles:
    print('Engineering Roles Detected:')
    for emp in eng_roles[:5]:
        print(f\"  - {emp['name']}: {emp['title']}\")
else:
    print('No engineering roles detected.')
"
        echo "════════════════════════════════════════════════════════════════"
        echo ""
        exit 0
    fi

    echo -n "."
done

kill $LOGS_PID 2>/dev/null || true

echo ""
echo -e "${YELLOW}⚠${NC} Task still running after 5 minutes"
echo "Check Celery Flower UI for task status: http://localhost:5555"
echo "Or check worker logs: docker compose logs worker"
