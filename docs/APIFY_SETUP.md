# Apify LinkedIn Setup Guide

## What is Apify?

Apify is a web scraping and automation platform that provides pre-built "Actors" (scraping scripts) for popular platforms like LinkedIn, Facebook, Twitter, etc.

For this project, we use **Apify LinkedIn Company Scraper** to extract:
- Company employee count
- Company description and specialties
- Industry classification
- Employee profiles and job titles
- Engineering roles detection

## Why Apify instead of direct scraping?

1. **LinkedIn blocks automated scraping** - they have aggressive anti-bot measures
2. **Apify handles proxies and sessions** - you don't need to manage IP rotation
3. **Pre-built LinkedIn scraper** - saves weeks of development time
4. **Legal compliance** - Apify manages LinkedIn's terms of service
5. **Quota management** - controlled usage to avoid bans

## Getting Your Apify API Token

### Step 1: Create Apify Account

1. Go to https://apify.com
2. Click "Sign Up" (free tier available)
3. Verify your email

### Step 2: Get API Token

1. Log in to Apify Console
2. Click your profile icon (top right)
3. Select "Settings"
4. Go to "Integrations" tab
5. Find "API token" section
6. Copy your personal API token

### Step 3: Add to .env

Open `/home/rayhanenouri/projects/abbk-leadengine/.env` and add:

```bash
APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Apify Pricing

### Free Tier (Good for Testing)
- **$5 free credits per month**
- LinkedIn Company Scraper: ~$0.25 per 100 companies
- Free tier = ~2,000 companies per month
- Perfect for development and testing

### Paid Plans (For Production)
- **Starter**: $49/month - 200 platform credits (~80,000 companies)
- **Team**: $499/month - 2,500 platform credits (~1M companies)
- **Enterprise**: Custom pricing

For ABBK LeadEngine demo and initial deployment, **free tier is sufficient**.

## How Our Integration Works

### Automatic Enrichment (Celery Beat)

The system automatically enriches LinkedIn data every 48 hours:

```python
# Runs every 2 days at midnight
"apify-linkedin-enrichment-48h": {
    "task": "apify_linkedin.enrich_all_leads",
    "schedule": crontab(minute=0, hour=0, day_of_week="*/2"),
}
```

This task:
1. Finds all leads with LinkedIn URLs
2. Skips recently enriched leads (last 7 days)
3. Calls Apify LinkedIn Company Scraper
4. Saves employee data to `lead.scraped_data.linkedin`
5. Detects engineering roles and creates signals
6. Updates employee count

### Manual Enrichment (API Endpoint)

You can also trigger enrichment for a single lead:

```bash
POST /api/leads/{lead_id}/enrich-linkedin
```

This is useful when:
- A new lead is added manually
- You want to refresh specific company data
- Testing the integration

### Data Stored

After enrichment, each lead's `scraped_data` contains:

```json
{
  "linkedin": {
    "scraped_at": "2026-06-21T10:30:00",
    "employee_count": 1500,
    "description": "Leading industrial group in Tunisia...",
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
      // ... up to 100 employees
    ]
  }
}
```

### Engineering Role Detection

The system automatically detects engineering roles using keywords:

- ingénieur, engineer
- conception, design
- CAD, bureau d'études
- R&D, recherche, développement
- mécanique, mechanical
- simulation, calcul
- fabrication, manufacturing

When engineering roles are found, a `role_detected` signal is created:

```
Signal: "15 engineering roles found on LinkedIn"
Detail: "Ahmed Ben Ali - Ingénieur conception, Sarah Trabelsi - CAD Designer, ..."
```

## Testing the Integration

### 1. Install Dependencies

```bash
cd /home/rayhanenouri/projects/abbk-leadengine
docker compose down
docker compose build backend worker
docker compose up -d
```

### 2. Add API Token

Edit `.env` and add your `APIFY_API_TOKEN`

### 3. Test Manual Enrichment

```bash
# Find a lead with LinkedIn URL
curl http://localhost:8000/api/leads?limit=10

# Trigger enrichment
curl -X POST http://localhost:8000/api/leads/1/enrich-linkedin \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Check result
curl http://localhost:8000/api/leads/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. Monitor Celery Worker

```bash
# Watch worker logs
docker compose logs -f worker

# Check Flower UI
open http://localhost:5555
```

## Rate Limiting & Best Practices

### Avoid Quota Exhaustion

1. **7-day cache**: System skips leads enriched in last 7 days
2. **2-second delay**: Waits between each scrape to avoid spamming
3. **48-hour schedule**: Automatic enrichment runs every 2 days, not daily

### Monitor Usage

Check your Apify usage:
1. Go to https://console.apify.com
2. Click "Usage" in sidebar
3. See credit consumption per day

### Optimize for Free Tier

For 2,000 companies/month on free tier:
- ~65 companies per day
- Current setting: enriches all leads every 48 hours
- If you have 100 leads = 50 enrichments/day ✅
- If you have 500 leads = 250 enrichments/day ❌ (need paid plan)

## Troubleshooting

### Error: "APIFY_API_TOKEN not set"

**Solution**: Add token to `.env` and restart containers:

```bash
docker compose restart worker beat
```

### Error: "apify-client not installed"

**Solution**: Rebuild backend container:

```bash
docker compose build backend worker
docker compose up -d
```

### Error: "No LinkedIn data returned"

**Possible causes**:
1. Invalid LinkedIn URL
2. Company page doesn't exist
3. LinkedIn privacy settings block scraping
4. Apify quota exhausted

**Solution**: Check Apify console for task details

### Enrichment Takes Too Long

**Normal**: Apify can take 30-120 seconds per company
**If stuck**: Check Celery worker logs for errors

## Alternative: LinkedIn Scraper CLI

If Apify is too expensive, you can use open-source alternatives:

1. **linkedin-api** (Python library) - requires LinkedIn account
2. **PhantomBuster** - similar to Apify, different pricing
3. **ScrapingBee** - general web scraping API

However, Apify is recommended for production use due to reliability and legal compliance.

## Next Steps

1. ✅ Get Apify API token
2. ✅ Add to `.env`
3. ✅ Rebuild Docker containers
4. ✅ Test with 1-2 leads
5. ✅ Monitor quota usage
6. ✅ Verify engineering role detection
7. ✅ Schedule runs production (free tier = every 48h)

## Questions?

- Apify Docs: https://docs.apify.com
- LinkedIn Scraper: https://apify.com/apify/linkedin-company-scraper
- Support: contact@apify.com
