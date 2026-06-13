# ABBK LeadEngine — Complete Project Context

## What this project is
AI-powered B2B lead generation and sales intelligence platform for ABBK Physicsworks — the official SolidWorks representative in Tunisia and North/West Africa. The platform automatically finds, enriches, scores, and ranks potential client companies so the sales manager knows exactly who to call, what to offer, and why they will say yes.

## Business goal
Replace the manager's current inefficient manual process — he currently googles SolidWorks Tunisia on the SolidWorks website, sees a database of names, and manually reviews them one by one. This platform automates everything: finding companies, enriching their profiles, scoring them per service, and ranking them by best opportunity. Primary success metric: number of qualified leads that become real sales.

## Geographic scope
- Primary: Tunisia
- Secondary: North Africa (Algeria, Morocco, Libya)
- Extended: West Africa and all African markets where ABBK can sell

## ABBK services (each gets its own independent score per lead)
1. SolidWorks license — main product
2. Other engineering software licenses (SIMULIA, CATIA, 3DEXPERIENCE)
3. Professional training programs on SolidWorks and engineering software

## Priority lead types (highest conversion — score these highest)
1. Multinational companies with international clients — their international clients FORCE them to use licensed software. Best conversion.
2. Companies under international audit — cannot use cracked software. Must buy license.
3. Companies with mechanical engineers, CAD designers, bureau d'études, R&D departments — they directly need SolidWorks.
4. Companies that did technical/engineering training recently — warm leads for ABBK training sales.
5. Companies attending engineering events and salons — already interested in the domain.
6. Companies that received international funding (bailleurs de fonds) — audited, must use real software.

## Important business context about cracked SolidWorks users
When ABBK calls companies using cracked versions, most hang up because they fear legal action. Strategy:
- Still detect potential cracked users (signal: has engineers but no license signals)
- Score them LOWER for direct license sales due to low conversion
- Score them HIGHER if they also have multinational/audit signals
- Never ignore them — they are leads, just lower priority
- Best approach for cracked users: lead with training offer first, not license

## Lead profile — what each company page must show
- Full company overview: name, sector, size, city, country, website, LinkedIn
- All enriched data: fiscalité, registre de commerce, actualité, nombre d'employés, nouveaux employés, type d'employés
- Score card: one score (0-100) per ABBK service with reasoning
- Overall recommendation: what is the single best deal to propose to this company and why
- Signals timeline: chronological list of all detected events
- Source links: where each piece of data came from

## Scoring system (fully automated — no manual input ever)
- Rule-based weighted scoring
- Each signal is boolean (true/false) extracted by Claude API
- Each signal has a different weight per service type
- Score = (sum of fired signal weights / total possible weights) * 100
- Score range: 0 to 100
- One score row per lead per ABBK service in lead_scores table
- Overall lead score = best opportunity across all services
- Scores recalculate automatically every time new data arrives
- Claude API responses cached in DB — never re-call same text twice

## Data sources to scrape (always dynamic, always updating)
Directories: annuaire.tn, pagesjaunes.tn, kompass.tn, registre national des entreprises
Job boards: emploi.tn, keejob.com, LinkedIn Jobs — target roles: ingénieur conception, CAD designer, bureau d'études, R&D, mécanique, production
News: businessnews.com.tn, managers.com.tn, tekiano.com
Training centers: ISET websites, université partner pages, centres de formation
Funding: Banque Mondiale, AFD, BEI, EU programs, USAID
Public sector: TUNEPS, Ministère de l'Industrie, Ministère de l'Enseignement Supérieur
Company websites: SolidWorks logo detection, SIMULIA/CATIA logos, job titles via Playwright
LinkedIn: Apify LinkedIn Company Scraper — employee roles, counts, recent hires
Events: engineering salons, SolidWorks events, industry conferences Tunisia and Africa

## Tech stack (final — do not change)
- Backend: FastAPI Python — port 8000
- Frontend: React + Vite + Tailwind CSS — port 5173
- Database: PostgreSQL 16 with pgvector — port 5432
- Cache + broker: Redis 7 — port 6379
- Task queue: Celery workers + Celery Beat
- Scraping: Scrapy + Playwright + Apify
- AI: Claude API claude-sonnet-4-5
- Containers: Docker Compose 7 services
- Hosting: Hetzner VPS CX31 Ubuntu 24.04
- Version control: GitHub rayhanenouri/abbk-leadengine branch develop

## Database tables (created and migrated — M1 complete)
users: id, email, full_name, hashed_pw, role (admin/manager/sales/viewer), permissions JSON, is_active
leads: id, company_name, website, linkedin_url, country, city, sector, employee_count, is_multinational, is_exporter, under_audit, scraped_data JSON, status, created_at, updated_at
lead_scores: id, lead_id FK, service_type, service_name, score float 0-100, reasoning text, signal_breakdown JSON, scored_at
lead_signals: id, lead_id FK, signal_type (new_hire/funding/news/logo_detected/role_detected/training_detected/event_attendance/tender_detected/funded/audit_signal), title, detail, source_url, detected_at
services: id, name, service_type, description, scoring_weights JSON, is_active

## M1 complete — built and working
- Docker Compose: all 7 services boot correctly
- FastAPI: GET /health returns 200
- PostgreSQL: 5 tables created via Alembic
- JWT auth: POST /api/auth/login returns token
- Protected routes: 401 without token, 403 wrong role
- RBAC: 4 roles enforced
- React frontend: boots on localhost:5173
- Test admin: admin@abbk.tn / admin123

## Known issues from M1
- Flower has import error — non-critical
- Nginx port 80 conflict — stopped for dev
- Issue 9 Hetzner deploy — pending M4

## Current milestone: M2 — Scraping engine
Due: June 16 2026
Demo to manager: June 20 2026
Final delivery: June 30 2026

## M2 priority order
1. Issue 11 — POST /api/leads/import CSV import
2. Issue 1 — Spider 1 directories
3. Issue 14 — Deduplication pipeline
4. Issue 16 — GET /api/leads with filters
5. Issue 10 — Apify LinkedIn
6. Issue 2 — Spider 2 job boards
7. Issue 3 — Spider 3 news
8. Issue 7 — Logo detection

## RBAC
- Admin: full access + user management
- Manager: all leads + scores + reports
- Sales: assigned leads only
- Viewer: read-only no scores

## Coding rules
- Always async/await for DB operations
- Always Pydantic schemas for request/response
- Always check duplicates before inserting leads
- Always store raw data in lead.scraped_data JSON
- Always create LeadSignal for every detected signal
- Never hardcode credentials — use .env settings
- Always add Celery tasks to beat_schedule
- Always create Alembic migration when changing models
- Cache Claude API responses in DB
- Commit format: feat: / fix: / chore:

## How to start every Claude Code session
1. docker compose up -d
2. docker compose ps
3. Read PROGRESS.md
4. Continue from current priority issue

## Developer
Final-year electrical engineering student. Python basics. Fast learner. Strong prompter. Ubuntu 24.04 LTS. 10 hours/day. Goal: deliver working LeadEngine, secure Dassault Systèmes internship.
