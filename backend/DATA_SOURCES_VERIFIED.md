# ABBK LeadEngine Data Sources — VERIFIED URLS ONLY

This document maps all **VERIFIED** data sources to their corresponding scrapers.

**Last updated**: 2026-06-24  
**Status**: Updated with client-verified URLs only. Old non-existent URLs removed.

---

## Overview — 34 Verified Data Sources

| Category | Count | Spider | Priority |
|----------|-------|--------|----------|
| Business Directories | 12 | directories_spider.py | HIGH |
| Job Boards | 9 | jobs_spider.py | HIGH |
| News & Press | 3 | news_spider.py | MEDIUM |
| Training & Education | 7 | training_spider.py | MEDIUM |
| LinkedIn Companies | 3 | linkedin_companies_spider.py | LOW (use Apify) |

---

## 1. Business Directories (12 sources)

**Spider**: `directories_spider.py`  
**Runner**: `backend/run_directories_spider.py`  
**Signal types**: Company profile, sector, location, size

### Tunisia-Specific Directories
1. https://mecatronic.tn/membres/ — Mecatronic industry association members
2. https://taa.tn/fr/membres — TAA (Tunisian automotive association) members
3. https://www.cetime.tn/fr/annuaire-des-entreprises — CETIME enterprise directory
4. https://www.tunisieindustrie.nat.tn/fr/dbi.asp — Tunisia industry database
5. https://www.tunisieindustrie.nat.tn/fr/dbs.asp — Tunisia services database
6. https://www.tunisieindustrie.nat.tn/fr/certifdbi.asp?action=list&idsect=&pagenum=1 — Certified companies
7. https://tn.kompass.com/en — Kompass Tunisia directory
8. https://www.scribd.com/document/620128474/Liste-Entreprises — Tunisia enterprise list

### Africa-Wide Directories
9. https://maps.prodafrica.com/ — Production Africa business map
10. https://africabusinessbureau.com/ — African business directory
11. https://www.success.ai/company-directory/Civil_Engineering/country/tunisia — Engineering companies Tunisia
12. https://www.aihitdata.com/search/companies?i=african+engineering — African engineering companies

---

## 2. Job Boards (9 sources)

**Spider**: `jobs_spider.py`  
**Runner**: `backend/run_jobs_spider.py`  
**Signal types**: `new_hire` (hiring signals)

### Tunisia Job Sites
1. https://www.naukrigulf.com/engineer-jobs-in-tunis — Engineering jobs Tunis
2. https://tunisia.tanqeeb.com/s/jobs/engineer?state=148 — Engineer jobs Tunisia
3. https://www.bayt.com/en/tunisia/jobs/mechanical-engineer-jobs/ — Mechanical engineer jobs
4. https://www.tunisietravail.net/ — Tunisia work portal
5. https://www.optioncarriere.tn/ — Career options Tunisia
6. https://www.keejob.com/ — KeeJob Tunisia
7. https://emploi.nat.tn/fo/Fr/global.php — National employment portal
8. https://www.tanitjobs.com/ — Tanit Jobs

### Africa Job Sites
9. https://www.africareers.net/ — African careers portal

**Target roles detected**: Ingénieur conception, CAD designer, Bureau d'études, R&D, Mécanique, Simulation, Fabrication, SOLIDWORKS

---

## 3. News & Press (3 sources)

**Spider**: `news_spider.py`  
**Runner**: `backend/run_news_spider.py`  
**Signal types**: `funding`, `news`, `export_signal`, `audit_signal`, `multinational_signal`

### Tunisia Business News
1. https://en.africanmanager.com/fdi-in-tunisia-rising-attractiveness-and-strategic-growth/ — African Manager
2. https://www.tunisieindustrie.nat.tn/en/etrangere.asp — Foreign investment news

### International/Africa News
3. https://www.adendorff.co.za/adendorff-optimum-cnc-machines-now-in-south-africa — South Africa CNC news

---

## 4. Training & Education (7 sources)

**Spider**: `training_spider.py`  
**Runner**: `backend/run_training_spider.py`  
**Signal types**: `training_detected`

### Engineering Schools
1. https://enis.rnu.tn/ — ENIS Sfax
2. https://enit.rnu.tn/en/presentation-2/ — ENIT Tunis
3. http://www.enicarthage.rnu.tn/en/ecole/apropos — ENIC Carthage

### Universities & Events
4. https://ucar.rnu.tn/events-et-news/ — UCAR events and news
5. https://www.ept.tn/news-and-events — EPT news and events

### Training Providers (Tunisia and Africa)
6. https://mecadtechnologies.co.za/specialised-training/ — Mecad Technologies (South Africa)
7. https://camining.com/ — CAMining training

---

## 5. LinkedIn Company Pages (3 sources)

**Spider**: `linkedin_companies_spider.py`  
**Runner**: `backend/run_linkedin_spider.py`  
**Signal types**: Company profile, LinkedIn enrichment

**⚠️ WARNING**: Direct LinkedIn scraping is heavily rate-limited.  
**RECOMMENDED**: Use Apify LinkedIn Company Scraper instead (see section below).

### Verified LinkedIn URLs
1. https://www.linkedin.com/company/m-c-engineering1/ — M-C Engineering
2. https://www.linkedin.com/company/lagos-swug/ — Lagos SOLIDWORKS User Group
3. https://community.swugn.org/tanzania-solidworks-user-group/ — Tanzania SOLIDWORKS User Group

---

## 6. LinkedIn via Apify (RECOMMENDED)

**Integration**: Apify LinkedIn Company Scraper  
**API Task**: `backend/app/workers/tasks/apify_discover.py`  
**API Route**: `backend/app/api/routes/apify.py`  
**Endpoint**: `POST /api/apify/discover`  
**Signal types**: `role_detected`, `new_hire`, company enrichment

### Data Extracted
- Company employee count
- Recent hires (job titles and engineering roles)
- Company description and specialties
- Industry classification
- Engineering role detection (CAD, SOLIDWORKS, Bureau d'études, etc.)

### Example API Call
```bash
curl -X POST http://localhost:8000/api/apify/discover \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SOLIDWORKS Tunisia",
    "max_results": 10
  }'
```

**Why Apify is better**: No rate limits, structured data, recent hires included, employee count accurate.

---

## Data Sources Removed (Non-Existent)

The following URLs were in the old spiders but have been **REMOVED** because they don't exist or are not verified:

### Removed from directories_spider.py
- annuaire.tn/cat/bureaux-d-etudes.html
- pagesjaunes.tn/entreprises/* (all old URLs)

### Removed from jobs_spider.py
- emploi.tn/recherche-jobs-tunisie (old URL format)

### Removed from news_spider.py
- businessnews.com.tn
- managers.com.tn
- tekiano.com

### Removed from training_spider.py
- All 12 ISET campus URLs (isetso.rnu.tn, isetrad.rnu.tn, etc.)
- atfp.tn
- tunisieformation.com
- formation.com.tn

---

## Data Pipeline Flow

```
1. Scrapy Spiders (5 spiders: directories, jobs, news, training, linkedin)
   ↓
2. Celery Task: scraping.py (process scraped data)
   ↓
3. Data Deduplication (by website OR company_name)
   ↓
4. Create/Update Lead in DB (leads table)
   ↓
5. Store raw data in lead.scraped_data JSON column
   ↓
6. Create LeadSignal records (lead_signals table)
   ↓
7. Trigger: Celery Task scoring.py
   ↓
8. Claude API: Extract signals from unstructured text
   ↓
9. Rule-based scoring per ABBK product (scoring_engine.py)
   ↓
10. Store scores in lead_scores table
```

---

## Automation Schedule (Celery Beat)

All scrapers run automatically via `backend/app/workers/celery_app.py`:

- **Directories spider**: Daily at 2 AM
- **Jobs spider**: Every 6 hours (hiring signals change fast)
- **News spider**: Every 12 hours
- **Training spider**: Weekly (Sunday 1 AM)
- **LinkedIn spider**: Manual only (use Apify instead)
- **Apify LinkedIn**: On-demand via API (no auto-schedule, rate limits apply)

---

## Testing Individual Spiders

```bash
# Test directories spider (12 sources)
cd backend
python run_directories_spider.py

# Test jobs spider (9 sources)
python run_jobs_spider.py

# Test news spider (3 sources)
python run_news_spider.py

# Test training spider (7 sources)
python run_training_spider.py

# Test LinkedIn spider (3 sources) — NOT RECOMMENDED, use Apify
python run_linkedin_spider.py

# Test Apify LinkedIn (RECOMMENDED, requires APIFY_API_TOKEN in .env)
curl -X POST http://localhost:8000/api/apify/discover \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "SOLIDWORKS Tunisia", "max_results": 10}'
```

---

## Monitoring Scrapers

```bash
# Watch Celery worker logs
docker compose logs -f abbk_worker

# Celery Flower UI (after fixing import error in M4)
open http://localhost:5555

# Check last scraping runs
curl http://localhost:8000/api/scraping/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Future Expansion (Post-June 30)

### Additional Countries
- **Algeria**: Expand directories, jobs, news to Algeria
- **Morocco**: Add Moroccan business directories and job boards
- **Libya, Egypt**: North Africa expansion
- **Nigeria, Ghana, Kenya**: West/East Africa engineering companies

### Additional Data Sources
- **Company websites** (Playwright): Logo detection, About page scraping
- **Tender platforms**: TUNEPS and ministry tenders (may require auth)
- **Event platforms**: Engineering salons and conferences
- **International funders**: World Bank, AFD, BEI, USAID Tunisia projects

### Data Quality Improvements
- **Website verification**: Ping all company websites to verify they exist
- **Email extraction**: Find contact emails from company websites
- **Phone normalization**: Standardize phone number formats
- **Geocoding**: Add latitude/longitude for map visualization

---

## Summary Statistics (Current)

- **Total verified sources**: 34
- **Spiders implemented**: 5 (directories, jobs, news, training, linkedin_companies)
- **Apify integration**: ✅ LinkedIn Company Scraper
- **Automation**: ✅ Celery Beat scheduled tasks
- **Deduplication**: ✅ By website OR company_name
- **Signal extraction**: ✅ Claude API claude-sonnet-4-5
- **Scoring engine**: ✅ Rule-based per ABBK product
- **Frontend**: ✅ Professional B2B dashboard

**Status**: Ready for June 20 demo (4 days away!)

---

End of DATA_SOURCES_VERIFIED.md
