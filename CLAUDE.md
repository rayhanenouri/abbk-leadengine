# ABBK LeadEngine — Complete Project Bible

## Project Identity
Name: ABBK LeadEngine
Type: AI-powered B2B lead generation and sales intelligence platform
Client: ABBK Physicsworks — official SolidWorks representative in Tunisia and North/West Africa
Developer: Rayhane Nouri — final-year electrical engineering student, Ubuntu 24.04 LTS
Repository: rayhanenouri/abbk-leadengine (private, branch: develop)
Demo deadline: June 20, 2026 to ABBK business manager
Final delivery: June 30, 2026

## The Problem We Are Solving
The ABBK sales manager currently:
- Manually googles SolidWorks Tunisia on the SolidWorks website
- Sees a database of company names and manually reviews them one by one
- Calls companies blindly without knowing if they are ready to buy
- When calling cracked SolidWorks users, most hang up fearing legal action
- Has no system to track signals, score leads, or prioritize who to call
This platform replaces all of that with full automation.

## Business Goal
Primary success metric: number of qualified leads that become real sales.
The manager opens the platform on his phone or computer and sees exactly which company to call today, what to offer them, and why they will say yes.

## Geographic Scope
- Primary: Tunisia
- Secondary: North Africa (Algeria, Morocco, Libya, Egypt)
- Extended: West Africa and all African markets where ABBK sells

## ABBK Exact Products and Services (verified from official website abbk-tn.com)

### Software Licenses ABBK sells (each gets its own score per lead):
1. SOLIDWORKS — main CAD 3D product
2. SOLIDWORKS Simulation — FEA structural analysis
3. SOLIDWORKS Flow Simulation — fluid dynamics and thermal
4. SOLIDWORKS Plastics — injection molding simulation
5. SOLIDWORKS PDM — product data management
6. SOLIDWORKS CAM + CAMWorks — manufacturing and machining
7. SOLIDWORKS Electrical — electrical system design
8. SOLIDWORKS Industrial Designer — industrial design
9. SOLIDWORKS Conceptual Designer — concept creation
10. Abaqus — advanced simulation (part of Simulia)
11. Simulia suite — simulation platform
12. 3DEXPERIENCE platform — cloud collaboration
13. EMWorks products — electromagnetic simulation

### Training Programs ABBK offers (each gets its own score per lead):
1. SOLIDWORKS Essential Level 1 training
2. SOLIDWORKS professional training
3. SOLIDWORKS certification preparation (CSWA, CSWP, CSWPA)
4. Abaqus training
5. CAMWorks training
6. 3DEXPERIENCE training
7. STEM Education programs for schools and universities
8. Corporate training programs

## Priority Lead Types (score these highest — best conversion)
### BASED ON BUSINESS MANAGER INPUT - EXACT WEIGHTS:

1. **HIGHEST PRIORITY: Training Potential** (40 points)
   - Companies that attended training or sent employees to technical training
   - Education institutions (universities, ISET, engineering schools)
   - Reason: ABBK training programs are the PRIMARY revenue stream
   - Strategy: Offer SOLIDWORKS Essential Level 1, CSWA certification prep

2. **HIGH PRIORITY: New Machine Purchase** (30 points - tender, 25 points - news)
   - Companies winning public tenders for new machines/equipment
   - Companies mentioned in news for expansion, new projects, new machines
   - Reason: New equipment = need new software licenses + training
   - Strategy: Bundle SOLIDWORKS license with training package

3. **HIGH PRIORITY: Hiring Engineers** (20 points each)
   - Companies actively hiring mechanical engineers, CAD designers, bureau d'études
   - Companies with engineering roles detected on website/LinkedIn
   - Reason: New engineers = immediate need for software + training
   - Strategy: Offer new hire training packages

4. **MEDIUM PRIORITY: Compliance & Export** (15 points each)
   - Multinational companies with international clients
   - Companies under international audit (ISO certification)
   - Companies with export activity
   - Companies with international funding (bailleurs de fonds)
   - Reason: International standards force licensed software usage
   - Strategy: Emphasize compliance and audit-readiness

5. **SUPPORTING SIGNALS** (10 points each)
   - Event attendance at engineering salons/conferences
   - SOLIDWORKS logo detected on website (potential upgrade opportunity)
   - Reason: Shows engagement and existing CAD software usage
   - Strategy: Upsell training, newer versions, additional modules

6. **SPECIAL CASE: Cracked Software Users** (detected but lower priority)
   - Companies with engineers but no license signals
   - Strategy: NEVER lead with legal threats
   - Strategy: Lead with training offer first, then upsell license
   - Reason: Fear of legal action causes them to hang up

## Important Business Context — Cracked SOLIDWORKS Users
When ABBK calls companies using cracked versions most hang up because they fear legal action. Strategy:
- Detect potential cracked users (signal: has engineers but no license signals)
- Score them LOWER for direct license sales due to low conversion rate
- Score them HIGHER if they also have multinational or audit signals
- Never ignore them — they are leads just lower priority
- Best approach: lead with training offer first then upsell license

## Complete Lead Profile — What Each Company Page Must Show
- Company overview: name, sector, size, city, country, website, LinkedIn URL
- Enriched data: fiscalite, registre de commerce, actualite, nombre employes, nouveaux employes, type employes, news recentes
- Score card: one score 0-100 per ABBK product and training with full reasoning
- Overall recommendation: single best deal to propose and why
- Signals timeline: all detected events chronological with source URLs
- Action suggestion: what to do next — call, wait, send info

## Scoring System (rule-based, fully automated, zero manual input ever)
Location: backend/app/services/scoring_engine.py

### Exact Signal Weights (Updated by Business Manager):
```
training_detected:    40 points  🎯 HIGHEST - Primary revenue stream
tender_detected:      30 points  💰 HIGH - New machine purchase signals
news:                 25 points  📰 HIGH - Expansion/new project signals  
new_hire:             20 points  👔 HIGH - Hiring engineers NOW
role_detected:        20 points  👔 HIGH - Engineering roles on website
is_multinational:     15 points  🌍 MEDIUM - International compliance needs
under_audit:          15 points  ✅ MEDIUM - Must use licensed software
is_exporter:          15 points  📦 MEDIUM - Export compliance required
funding:              15 points  💵 MEDIUM - International funding received
event_attendance:     10 points  🎪 Supporting - Industry engagement
logo_detected:        10 points  👁️ Supporting - CAD software detected

Maximum possible:     215 points
```

### Calculation Logic:
- Each signal is boolean true or false
- Claude API extracts signals from unstructured scraped text
- Score = (sum of fired signal weights / 215) × 100
- Score range 0 to 100
- One row in lead_scores per lead per ABBK product and per training
- Overall lead score = best opportunity across all products
- Scores auto-recalculate every time new data arrives via Celery task
- Claude API responses cached in DB — never re-call same text twice

### Score Classification:
- 70-100: 🔥 HOT - Call today
- 60-69:  🔶 WARM - Call this week  
- 30-59:  📋 POTENTIAL - Add to pipeline
- 0-29:   🔍 RESEARCH - Gather more data

## Signal Types (stored in lead_signals table)
Sorted by business priority (weight in parentheses):

**Priority 1 - Training (40pts)**:
- training_detected: company sent employees to technical training, attended SOLIDWORKS days, ISET partnerships

**Priority 2 - New Machines & Hiring (20-30pts)**:
- tender_detected: won public tender for new machines/equipment (30pts)
- news: mentioned in press for expansion, new machines, new projects (25pts)
- new_hire: actively hiring mechanical engineers, CAD designers, bureau d'études (20pts)
- role_detected: engineering job titles found on website or LinkedIn (20pts)

**Priority 3 - Compliance & International (15pts each)**:
- is_multinational: has international clients or parent company
- under_audit: ISO certification, international audit, compliance requirements
- is_exporter: exports products internationally
- funding: received international funding (World Bank, AFD, EU, etc.)

**Priority 4 - Supporting Signals (10pts each)**:
- event_attendance: attended engineering events, salons, conferences
- logo_detected: SOLIDWORKS, Simulia, Abaqus, 3DEXPERIENCE, or competitor CAD found on website

**Special Detection**:
- cracked_risk: has engineers but no license signals — potential unlicensed software user (LOWER priority, lead with training offer)

## Complete Data Sources to Scrape

### Business Directories
- annuaire.tn
- pagesjaunes.tn
- kompass.tn
- Registre national des entreprises Tunisia
- African business directories per country
- find any other trusted data sources that can bring me leads that we can convert into real sales. 

### Job Boards — Hiring Signals
- emploi.tn
- keejob.com
- LinkedIn Jobs via Apify
- Target roles: ingenieur conception, CAD designer, bureau d etudes, R&D, mecanique, production, ingenieur simulation, ingenieur calcul, ingenieur fabrication
- find any other trusted Hiring signals that can bring me leads that we can convert into real sales. 

### News and Press
- businessnews.com.tn
- managers.com.tn
- tekiano.com
- African business news sites
- find any other trusted news and press sources that can bring me leads that we can convert into real sales. 

### Training Centers
- ISET websites all regional campuses
- University partner pages
- Company training and HR sections
- Centres de formation professionnelle listings
- ATFP Agence Tunisienne de la Formation Professionnelle

### Bailleurs de Fonds and International Funding
- Banque Mondiale Tunisia projects
- AFD Agence Francaise de Developpement
- BEI Banque Europeenne d Investissement
- USAID Tunisia programs
- EU funding programs Tunisia and Africa
- GIZ Deutsche Gesellschaft fur Internationale Zusammenarbeit
- find any other trusted data sources that can bring me leads that we can convert into real sales. 

### Public Sector and Tenders
- TUNEPS Tunisian public procurement platform
- Ministere de l Industrie
- Ministere de l Enseignement Superieur et de la Recherche
- Other ministere tender platforms
- find any other trusted data sources that can bring me leads that we can convert into real sales. 

### Company Websites via Playwright
- SOLIDWORKS logo detection
- Simulia Abaqus 3DEXPERIENCE CAMWorks logo detection
- Engineering job titles in About and Team pages
- Products requiring engineering software mention


### LinkedIn via Apify (APIFY_API_TOKEN in .env)
- Apify LinkedIn Company Scraper
- Extract: employee count description specialties industry
- Recent hires and job titles
- Engineering roles detection

### Events and Conferences
- Engineering salons Tunisia and Africa
- SOLIDWORKS regional events and days
- Industry events automotive aerospace manufacturing construction
- University career fairs with engineering companies

### Research Centers
- Annuaire des centres de recherche Tunisia
- University research labs
- CRBT CERTE and other national research centers


## Tech Stack — Final Decisions Do Not Change
- Backend: FastAPI Python — port 8000
- Frontend: React 18 plus Vite plus Tailwind CSS — port 5173
- Database: PostgreSQL 16 with pgvector — port 5432
- Cache and broker: Redis 7 — port 6379
- Task queue: Celery workers plus Celery Beat
- Scraping structured sites: Scrapy
- Scraping JS-heavy sites: Playwright Chromium
- LinkedIn data: Apify LinkedIn Company and Jobs Scraper
- AI signal extraction: Claude API claude-sonnet-4-5
- Lead analysis text: Claude API for reasoning and recommendations
- Containers: Docker Compose 7 services
- Python packages: uv
- Hosting production: Hetzner VPS CX31 Ubuntu 24.04
- Version control: Git plus GitHub rayhanenouri/abbk-leadengine
- Branch: develop daily work then main when milestone complete

## Docker Services All 7
- abbk_backend: FastAPI port 8000
- abbk_frontend: React Vite port 5173
- abbk_db: PostgreSQL port 5432
- abbk_redis: Redis port 6379
- abbk_worker: Celery worker background scraping and scoring
- abbk_beat: Celery Beat scheduler triggers all automation
- abbk_flower: Celery monitoring UI port 5555 has import bug fix in M4

## Database Schema All Tables Created in M1

### users
id, email, full_name, hashed_pw
role: admin or manager or sales or viewer
is_active: boolean
permissions: JSON per-section read write none
created_at

### leads
id, company_name, website, linkedin_url
country, city, sector
employee_count, is_multinational, is_exporter, under_audit
scraped_data: JSON all raw data from all sources
status: new qualified contacted converted lost
created_at, updated_at

### lead_scores
id, lead_id FK to leads
service_type, service_name
score: float 0 to 100
reasoning: text AI explanation
signal_breakdown: JSON which signals fired and their weights
scored_at

### lead_signals
id, lead_id FK to leads
signal_type, title, detail
source_url, detected_at

### services
id, name, service_type, description
scoring_weights: JSON signal to weight mapping
is_active

## Project Folder Structure
abbk-leadengine/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/config.py
│   │   ├── db/session.py
│   │   ├── models/models.py
│   │   ├── schemas/
│   │   ├── api/routes/
│   │   │   ├── auth.py
│   │   │   ├── leads.py
│   │   │   ├── users.py
│   │   │   ├── scores.py
│   │   │   └── scraping.py
│   │   ├── services/
│   │   │   └── scoring_engine.py
│   │   └── workers/
│   │       ├── celery_app.py
│   │       └── tasks/
│   │           ├── scraping.py
│   │           ├── scoring.py
│   │           └── enrichment.py
│   ├── alembic/
│   ├── Dockerfile
│   └── pyproject.toml
├── scraper/
│   ├── spiders/
│   │   ├── directories_spider.py
│   │   ├── jobs_spider.py
│   │   ├── news_spider.py
│   │   ├── training_spider.py
│   │   ├── funders_spider.py
│   │   └── tenders_spider.py
│   └── utils/
│       ├── dedup.py
│       ├── enrichment.py
│       └── logo_detector.py
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       └── api/
├── docker-compose.yml
├── CLAUDE.md
├── PROGRESS.md
├── SKILLS.md
└── .env never commit this

## Milestone Plan
M1 Foundation COMPLETE due June 9
M2 Scraping engine IN PROGRESS due June 16
M3 Scoring engine due June 22
M4 Dashboard plus deploy due June 28
M5 Deliver due June 30

## M1 Complete — What Works Right Now
- Docker Compose: all 7 services boot
- GET /health returns status ok version 0.1.0
- PostgreSQL: 5 tables created via Alembic
- POST /api/auth/login returns JWT token
- Protected routes: 401 without token 403 wrong role
- RBAC: 4 roles enforced with middleware
- React frontend boots on localhost:5173
- Test admin: admin@abbk.tn password admin123

## M2 Issues 16 Total — Priority Order for June 20 Demo

MUST HAVE FOR DEMO:
11 — POST /api/leads/import CSV import of ABBK existing database
1  — Spider 1 Tunisian directories annuaire.tn pagesjaunes.tn kompass.tn
14 — Data deduplication and multi-source merging pipeline
16 — GET /api/leads paginated filtered sorted with signals
10 — Apify LinkedIn connector

IMPORTANT FOR DEMO:
2  — Spider 2 job boards emploi.tn keejob.com hiring signals
3  — Spider 3 Tunisian business news signals
7  — Logo detection on company websites Playwright

COMPLETE AFTER DEMO:
4  — Spider 4 training history detection
5  — Spider 5 bailleurs de fonds
6  — Spider 6 ministeres and public tenders
8  — Multinational and exporter detection
9  — Audit pressure detection
12 — Company enrichment fiscalite actualite employes
13 — Event-based lead signals
15 — Celery Beat all scrapers auto-scheduled

## M3 Plan — Scoring Engine
- Rule-based weighted scoring per ABBK product and training
- Claude API signal extraction from scraped text
- Score recalculation Celery task after every scrape
- GET /api/scores endpoint
- Lead recommendation engine best deal per lead
- Score reasoning text generation via Claude API
- Seed services table with all ABBK products and their scoring weights

## M4 Plan — Dashboard and Deploy
- React dashboard: ranked leads list sorted by best score
- Lead profile page with full company analysis
- Score cards per ABBK product with reasoning text
- Signals timeline per company
- Admin panel: user management RBAC control
- Mobile responsive — manager uses phone
- Notification system: bell icon alerts for high-score signals
- Hetzner VPS deployment
- Nginx reverse proxy production config
- Fix Flower import error
- Fix Nginx port 80 conflict

## M5 Plan — Deliver
- Seed 20 to 30 real ABBK companies
- Run full scraping on real Tunisian data
- Verify scores make business sense
- Fix any bugs found during ABBK walkthrough
- Final Hetzner deployment confirmed working

## RBAC Rules
Admin: full access plus user management plus RBAC control
Manager: all leads plus all scores plus reports plus dashboard plus notifications
Sales: assigned leads only plus their scores no other user data
Viewer: read-only no scores visible

## Notification System Built in M4
Triggers: new_hire_engineer detected, funding_received, high_score_lead above 80, audit_signal_detected
Delivery: in-platform bell icon notifications
Storage: DB table so manager sees alerts on mobile
Future: email via SendGrid or Mailgun flexible integration

## Known Issues and Blockers
- Flower UI has import error non-critical fix M4
- Nginx port 80 conflict on local dev stopped fix M4
- Issue 9 Hetzner deploy pending M4
- Playwright not installed in Docker commented out reinstall M4
- APIFY_API_TOKEN empty in .env add before issue 10
- ANTHROPIC_API_KEY empty in .env add before M3

## Coding Rules Always Follow Without Exception
1. Always use async await for all DB operations SQLAlchemy async
2. Always use Pydantic schemas for every request and response
3. Always check duplicates before inserting any lead by website OR company_name
4. Always store raw scraped data in lead.scraped_data JSON column
5. Always create a LeadSignal record for every detected signal
6. Never hardcode credentials always use settings from core/config.py
7. Always add new Celery tasks to beat_schedule in celery_app.py
8. Always create Alembic migration when changing any model
9. Cache all Claude API responses in DB never re-call same text twice
10. Every route must be protected with get_current_user dependency
11. Every admin route must use require_role UserRole.admin
12. Commit format: feat: description or fix: description or chore: description
13. Close GitHub issues with: gh issue close N --comment explanation
14. Always push to develop branch: git push origin develop

## How to Start Every Claude Code Session
1. cd ~/projects/abbk-leadengine
2. docker compose up -d
3. docker compose ps verify all running
4. Read PROGRESS.md for exact current status
5. Continue from current priority issue in PROGRESS.md

## Developer Context
Name: Rayhane Nouri
Level: final-year electrical engineering student
Python: basic knowledge learning fast
Daily availability: 10 hours
Goal 1: deliver working LeadEngine to ABBK by June 30
Goal 2: secure internship at Dassault Systemes through this project
Uses: Claude Code daily for all development
Machine: Ubuntu 24.04 LTS
