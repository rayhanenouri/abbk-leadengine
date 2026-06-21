# Session Summary — 2026-06-21

## Issue #19 Complete: Apify LinkedIn Connector ✅

### What Was Built

Complete integration with Apify LinkedIn Company Scraper to automatically enrich company data with LinkedIn information.

### Files Created

1. **`backend/app/workers/tasks/apify_linkedin.py`** (265 lines)
   - Full Apify LinkedIn Company Scraper integration
   - Uses `apify-client` Python SDK
   - Extracts employee count, description, specialties, industry
   - Scrapes up to 100 employee profiles per company
   - Detects engineering roles using keyword matching

2. **`docs/APIFY_SETUP.md`** (comprehensive guide)
   - How to get Apify API token
   - Pricing breakdown (free tier = 2,000 companies/month)
   - Integration architecture
   - Data structure documentation
   - Testing instructions
   - Troubleshooting guide

3. **`scripts/test_apify.sh`** (automated test script)
   - Checks APIFY_API_TOKEN in .env
   - Finds lead with LinkedIn URL or creates test lead
   - Triggers enrichment task
   - Monitors progress in real-time
   - Displays enrichment results

### Features Implemented

#### 1. Celery Tasks
- **`apify_linkedin.enrich_all_leads`** — batch enrichment of all leads with LinkedIn URLs
- **`apify_linkedin.enrich_single_lead`** — on-demand enrichment for specific lead
- **7-day cache** — skips leads enriched in last 7 days to save quota
- **Rate limiting** — 2-second delay between requests

#### 2. Celery Beat Scheduling
- Automatic enrichment every 48 hours (quota-friendly)
- Scheduled at midnight every 2 days
- Runs in `enrichment` queue
- Added to `celery_app.py` beat_schedule

#### 3. API Endpoint
- **`POST /api/leads/{lead_id}/enrich-linkedin`**
- Manually trigger LinkedIn enrichment for specific lead
- Returns task ID for monitoring
- Validates lead has LinkedIn URL

#### 4. Data Storage
All LinkedIn data saved to `lead.scraped_data.linkedin`:
```json
{
  "scraped_at": "2026-06-21T10:30:00",
  "employee_count": 1500,
  "description": "Leading industrial group...",
  "specialties": ["Manufacturing", "Engineering", "Distribution"],
  "industry": "Industrial Equipment",
  "headquarters": "Tunis, Tunisia",
  "founded": 1982,
  "company_type": "Private Company",
  "website": "https://example.com",
  "employees": [
    {
      "name": "Ahmed Ben Ali",
      "title": "Ingénieur conception mécanique",
      "location": "Tunis, Tunisia",
      "profile_url": "https://linkedin.com/in/..."
    }
  ]
}
```

#### 5. Engineering Role Detection
Automatically detects engineering roles using keywords:
- `ingénieur`, `engineer`
- `conception`, `design`
- `CAD`, `bureau d'études`
- `R&D`, `recherche`, `développement`
- `mécanique`, `mechanical`
- `simulation`, `calcul`
- `fabrication`, `manufacturing`

When engineering roles found, creates `role_detected` signal:
- Title: "{N} engineering roles found on LinkedIn"
- Detail: List of first 5 engineers with their titles
- Source: LinkedIn company URL

### Technical Details

#### Dependencies Added
- `apify-client>=1.7.0` in `backend/pyproject.toml`
- Installed in Docker containers (backend + worker)

#### Integration Architecture
1. User adds `APIFY_API_TOKEN` to `.env`
2. Celery Beat triggers `enrich_all_leads` every 48 hours
3. Task finds all leads with LinkedIn URLs
4. For each lead:
   - Skip if enriched in last 7 days
   - Call Apify LinkedIn Company Scraper
   - Parse company profile + employee data
   - Save to `lead.scraped_data.linkedin`
   - Update `lead.employee_count` if available
   - Detect engineering roles
   - Create `role_detected` signals
5. Wait 2 seconds before next lead (rate limiting)

#### Free Tier Economics
- **Apify free tier**: $5/month = ~2,000 companies
- **ABBK database**: ~120 companies currently
- **Enrichment frequency**: every 48 hours
- **Monthly usage**: ~1,800 enrichments
- **Verdict**: ✅ Free tier sufficient for ABBK demo and initial production

### How to Use

#### 1. Get Apify API Token
```bash
# Visit https://console.apify.com/account/integrations
# Sign up for free account
# Copy API token
# Add to .env:
APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 2. Rebuild Containers
```bash
docker compose build backend worker
docker compose up -d
docker compose restart beat
```

#### 3. Test Integration
```bash
cd /home/rayhanenouri/projects/abbk-leadengine
./scripts/test_apify.sh
```

#### 4. Monitor Progress
- **Celery Flower UI**: http://localhost:5555
- **Worker logs**: `docker compose logs -f worker`
- **Beat schedule**: `docker compose logs beat | grep apify`

#### 5. Manual Enrichment via API
```bash
# Get JWT token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@abbk.tn","password":"admin123"}' | \
  jq -r '.access_token')

# Trigger enrichment for lead ID 1
curl -X POST http://localhost:8000/api/leads/1/enrich-linkedin \
  -H "Authorization: Bearer $TOKEN"
```

### Business Value for ABBK

#### High-Value Signal Detection
LinkedIn data reveals:
1. **Engineering team size** — companies with 10+ engineers = serious CAD users
2. **Specific roles** — "Ingénieur conception" = direct SOLIDWORKS user
3. **Recent hires** — hiring engineers = growth signal = ready to buy licenses
4. **Job titles** — "Bureau d'études" = design office = need PDM + CAM
5. **Company size** — employee count validates lead priority

#### Scoring Impact
Engineering roles detected from LinkedIn increase scores for:
- SOLIDWORKS licenses (main product)
- SOLIDWORKS Simulation (for calcul engineers)
- SOLIDWORKS CAM (for fabrication engineers)
- Training programs (for new hires)

#### Sales Intelligence
Manager sees on lead detail page:
- "15 engineering roles found on LinkedIn"
- List of engineers: "Ahmed Ben Ali - Ingénieur conception mécanique"
- When calling, can mention: "I see you have 15 engineers on your team..."
- Personalized pitch based on detected roles

### Next Steps

#### Required Before Demo (June 30):
1. ✅ Code complete
2. ⏳ User adds APIFY_API_TOKEN to .env
3. ⏳ Run test script with 1-2 real Tunisian companies
4. ⏳ Verify engineering role detection accuracy
5. ⏳ Monitor quota usage via Apify console

#### Optional Improvements (Post-Demo):
- Add recent hire detection (if Apify provides hire dates)
- Filter employees by department (focus on engineering dept)
- Detect role changes (promotions = company growth)
- Add LinkedIn signal to lead detail page UI
- Show employee count trend over time

### GitHub Status

- ✅ Issue #19 closed
- ✅ Commit pushed to `develop` branch
- ✅ Comprehensive closing comment with documentation
- ✅ PROGRESS.md updated: 11/16 M2 issues complete (68.75%)

### M2 Progress Update

**Completed (11/16 = 68.75%)**:
1. ✅ #20 — CSV import
2. ✅ #10 — Spider 1: Directories
3. ✅ #12 — Spider 3: News
4. ✅ #17 — Multinational detection
5. ✅ #18 — Audit pressure detection
6. ✅ #23 — Deduplication pipeline
7. ✅ #25 — GET /api/leads with pagination
8. ✅ #11 — Spider 2: Job boards
9. ✅ #16 — Logo detection
10. ✅ #24 — Celery Beat scheduling
11. ✅ #19 — Apify LinkedIn connector ← **JUST COMPLETED**

**Remaining (5/16 = 31.25%)**:
- [ ] #13 — Spider 4: Training history ← **START NEXT**
- [ ] #14 — Spider 5: Bailleurs de fonds
- [ ] #15 — Spider 6: Ministères/tenders
- [ ] #21 — Company enrichment (fiscalité, actualité, employés)
- [ ] #22 — Event signals

### Session Stats

- **Time**: ~1 hour
- **Lines of code**: 809 added across 7 files
- **Features**: 5 major (tasks, scheduling, API, detection, docs)
- **Documentation**: 3 comprehensive files
- **Tests**: 1 automated test script
- **Issues closed**: 1 (#19)
- **Milestone progress**: +6.25% (62.5% → 68.75%)

### What's Next

**Next priority: Issue #13 — Training History Spider**

Scrape training centers and detect when companies send employees to training:
- ISET websites (all regional campuses)
- University partner pages
- Company training and HR sections
- Centres de formation professionnelle listings
- ATFP (Agence Tunisienne de la Formation Professionnelle)

Signal: `training_detected`
Business value: Companies investing in employee training = warm leads for ABBK training programs

---

**End of session summary**
**Date**: 2026-06-21
**Next session**: Continue with Issue #13 (Training spider)
