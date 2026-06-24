# Apify LinkedIn Discovery - Complete Setup Guide

## What This Does 🎯

Automatically discovers **500+ Tunisian engineering and manufacturing companies** from LinkedIn using Apify's official API.

### Features:
- ✅ Finds companies by keyword search ("engineering Tunisia", "CAD Tunisia", etc.)
- ✅ Scrapes company profiles (name, industry, employees, description)
- ✅ Creates new Lead records automatically
- ✅ Detects engineering roles and creates signals
- ✅ No web scraping issues (uses official LinkedIn API)
- ✅ Guaranteed fresh data every time

---

## Prerequisites ✅

### 1. Apify Account
1. Sign up at **https://apify.com**
2. Get free $5 credit (enough for ~500 companies)
3. Copy your **API Token** from: https://console.apify.com/account/integrations

### 2. Apify Actors Needed
The system uses these Apify actors (no setup needed, just ensure you have credit):
- **apify/linkedin-search-companies-urls** - Finds company URLs
- **apify/linkedin-company-scraper** - Scrapes company profiles

### 3. Cost Estimate 💰
- **500 companies:** ~$3-5 USD
- **Per company:** ~$0.006-0.01 USD
- **Free tier:** $5 credit = 500-800 companies

---

## Setup Instructions 🛠️

### Step 1: Add API Token to .env

```bash
cd ~/projects/abbk-leadengine
nano .env
```

Add this line (replace with your actual token):

```
APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Save and exit (Ctrl+X, Y, Enter)

### Step 2: Restart Services

```bash
docker compose restart backend worker beat
```

### Step 3: Verify Setup

Check that containers are running:

```bash
docker compose ps
```

All services should show "Up" status.

---

## Usage 🚀

### Option 1: Automatic Trigger (Manual Test)

Run the test script:

```bash
cd ~/projects/abbk-leadengine/backend
python test_apify_discovery.py
```

This will:
1. Show current stats
2. Ask for confirmation
3. Trigger discovery task
4. Monitor progress (10-30 minutes)
5. Show results

### Option 2: API Trigger (For Dashboard Integration)

```bash
curl -X POST http://localhost:8000/api/apify/discover \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

Response:
```json
{
  "status": "started",
  "task_id": "abc123...",
  "message": "LinkedIn discovery started. This may take 10-30 minutes.",
  "estimated_results": "500+ companies",
  "check_status_at": "/api/apify/status/abc123..."
}
```

### Option 3: Scheduled Automatic Discovery

Already configured in Celery Beat! Runs **every Friday at 3am**.

Check schedule:

```bash
docker logs abbk_beat | grep apify
```

---

## How It Works 🔍

### Phase 1: Search LinkedIn (5-10 minutes)

Searches LinkedIn for companies matching these keywords:
- "engineering Tunisia"
- "bureau d'études Tunisie"
- "manufacturing Tunisia"
- "CAD Tunisia"
- "SOLIDWORKS Tunisia"
- "ingénierie mécanique Tunisie"
- "fabrication industrielle Tunisie"
- "construction Tunisia"
- "automotive Tunisia"
- "aerospace Tunisia"

**Result:** 500+ LinkedIn company URLs

### Phase 2: Scrape Profiles (10-20 minutes)

For each URL, Apify scrapes:
- Company name
- Industry/sector
- Employee count
- Description
- Headquarters location
- Website URL
- LinkedIn URL
- Specialties
- Company type

### Phase 3: Save to Database (1-2 minutes)

For each company:
1. Check if already exists (by name, LinkedIn URL, or website)
2. If new:
   - Create Lead record
   - Store all LinkedIn data in `scraped_data` JSON field
   - Create "linkedin_discovery" signal
   - Set status = "new"

### Phase 4: Score and Rank (automatic)

Celery Beat will automatically:
- Detect engineering roles
- Calculate scores for all ABBK services
- Flag multinationals, exporters, under_audit
- Generate recommendations

---

## API Endpoints 📡

### 1. Trigger Discovery

```
POST /api/apify/discover
Headers: Authorization: Bearer {token}
```

Discovers 500+ Tunisian companies.

### 2. Discover by Keyword

```
POST /api/apify/discover/keyword?keyword=SOLIDWORKS Tunisia&max_results=50
Headers: Authorization: Bearer {token}
```

Targeted search by custom keyword.

### 3. Check Task Status

```
GET /api/apify/status/{task_id}
Headers: Authorization: Bearer {token}
```

Returns: pending | running | completed | failed

### 4. Get Statistics

```
GET /api/apify/stats
Headers: Authorization: Bearer {token}
```

Returns LinkedIn enrichment stats.

### 5. Enrich Existing Leads

```
POST /api/apify/enrich
Headers: Authorization: Bearer {token}
```

Enriches all leads that already have LinkedIn URLs.

---

## Expected Results 📊

### Before:
- **Total leads:** 121
- **Last update:** June 20, 2026
- **Days stale:** 2

### After Discovery:
- **Total leads:** 621+ (500 new + 121 existing)
- **New signals:** 500+ linkedin_discovery signals
- **Employee data:** 500+ leads with employee counts
- **Engineering roles:** 200-300 leads with role_detected signals
- **Geographic distribution:** All Tunisian cities
- **Sectors:** Engineering, Manufacturing, Construction, Industrial, Automotive, etc.

### Sample New Lead:

```json
{
  "company_name": "Bureau d'Études Techniques SIGMA",
  "sector": "Engineering Services",
  "city": "Tunis",
  "country": "Tunisia",
  "employee_count": 45,
  "website": "https://sigma-engineering.tn",
  "linkedin_url": "https://linkedin.com/company/sigma-engineering-tn",
  "status": "new",
  "scraped_data": {
    "linkedin": {
      "scraped_at": "2026-06-22T15:30:00",
      "description": "Bureau d'études spécialisé en conception mécanique...",
      "specialties": ["CAD", "Simulation", "Manufacturing"],
      "industry": "Engineering Services",
      "follower_count": 1200
    }
  }
}
```

---

## Troubleshooting 🔧

### Issue: "APIFY_API_TOKEN not set"

**Solution:**
1. Check .env file has `APIFY_API_TOKEN=...`
2. Restart backend: `docker compose restart backend worker`
3. Verify: `docker exec abbk_backend printenv | grep APIFY`

### Issue: "apify-client not installed"

**Solution:**
```bash
docker compose down worker
docker compose up -d --build worker
```

### Issue: Task stuck on "pending"

**Solution:**
1. Check worker is running: `docker logs abbk_worker`
2. Check task was received: `docker logs abbk_worker | grep discover`
3. Restart worker: `docker compose restart worker`

### Issue: "No results found"

**Possible causes:**
- Apify credit exhausted (check https://console.apify.com)
- LinkedIn rate limiting (wait 1 hour)
- Network connectivity issue (check `docker exec abbk_worker curl https://api.apify.com`)

### Issue: Duplicate companies

The system automatically deduplicates by:
- Company name (exact match)
- LinkedIn URL
- Website URL

If duplicates appear, they have different values in all three fields.

---

## Cost Optimization 💡

### Free Tier Strategy:
1. Start with **50 companies** (keyword search with `max_results=50`)
2. Monitor cost at https://console.apify.com
3. Scale up if cost is acceptable

### Keyword Strategy:
Instead of 10 keywords × 50 results = 500 companies, try:
- **Targeted approach:** 3 best keywords × 100 results = 300 companies
- **High-value keywords:** "SOLIDWORKS Tunisia", "bureau d'études ingénierie", "CAD Tunisia"

### Schedule Strategy:
- Don't run discovery daily (expensive!)
- **Weekly** is enough for B2B leads (Fridays at 3am)
- **On-demand** when manager needs fresh data

---

## Integration with Dashboard 🖥️

### Next Steps:
1. Add "Refresh Data" button to dashboard
2. Button triggers: `POST /api/apify/discover`
3. Show progress modal with task status
4. Display "New Leads Discovered: 250" notification
5. Auto-refresh leads table

### Mockup:

```
┌─────────────────────────────────────┐
│  ABBK LeadEngine Dashboard         │
├─────────────────────────────────────┤
│                                     │
│  [🔄 Refresh Data]  [📊 Analytics] │
│                                     │
│  ┌─────────────────────────────┐  │
│  │  🔍 Discovering companies... │  │
│  │  Progress: 150 / 500        │  │
│  │  ETA: 15 minutes            │  │
│  └─────────────────────────────┘  │
│                                     │
│  📊 Total Leads: 621               │
│      ✨ 500 new this week          │
│                                     │
└─────────────────────────────────────┘
```

---

## Success Criteria ✅

Discovery is working correctly when:

1. ✅ Task status changes: pending → running → completed
2. ✅ Database shows 500+ new leads created today
3. ✅ New leads have LinkedIn data in `scraped_data` field
4. ✅ New leads have `linkedin_discovery` signals
5. ✅ Employee counts populated (most leads)
6. ✅ Sectors are engineering/manufacturing related
7. ✅ All leads have country="Tunisia"

---

## Next Steps After First Discovery 🚀

1. **Verify Data Quality**
   - Check company names are real businesses
   - Verify employee counts are reasonable
   - Confirm sectors match ABBK target

2. **Run Enrichment**
   - Detect multinational status
   - Detect audit pressure
   - Detect exporter status

3. **Calculate Scores**
   - Run scoring engine on all new leads
   - Rank by best opportunity

4. **Share with ABBK Manager**
   - Export top 50 leads to Excel
   - Show dashboard with ranked leads
   - Demonstrate search/filter features

5. **Set Up Automation**
   - Enable weekly Celery Beat schedule
   - Add dashboard refresh button
   - Configure notifications for high-score leads

---

## Support 📞

If you encounter issues:

1. Check logs: `docker logs abbk_worker`
2. Check Apify console: https://console.apify.com/actors/runs
3. Check database: `docker exec abbk_db psql -U abbk_user -d abbk_LeadEngine -c "SELECT COUNT(*) FROM leads WHERE created_at > NOW() - INTERVAL '1 day';"`
4. Run test script: `python test_apify_discovery.py`

---

**Ready to discover 500+ leads? Run the test script now!** 🚀

```bash
cd ~/projects/abbk-leadengine/backend
python test_apify_discovery.py
```
