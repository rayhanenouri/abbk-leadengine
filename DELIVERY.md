# ABBK LeadEngine — Project Delivery
## Delivered by: Rayhane Nouri
## Date: June 30, 2026
## Client: ABBK Physicsworks Tunisia

## What Was Built
A complete AI-powered B2B lead generation platform that replaces the manual prospecting process. The platform automatically finds Tunisian and African companies that are potential clients for ABBK's SolidWorks licenses and training programs, enriches their profiles with real data, and scores them per ABBK service so the sales manager knows exactly who to call and what to offer.

## Platform Access
Local: http://localhost:5173
Admin: admin@abbk.tn / admin123
API Docs: http://localhost:8000/docs

## How to Start the Platform
```bash
cd ~/projects/abbk-leadengine
docker compose up -d
```
Open http://localhost:5173

## What the Platform Does
1. Automatically scrapes 9 Tunisian data sources for potential leads
2. Enriches each company profile with real data from their website, job postings, news
3. Scores each company for all 21 ABBK products and training programs independently
4. Ranks leads by best opportunity — the manager sees who to call first
5. Shows real signals with source URLs proving why each company is a good lead
6. Works on desktop and mobile phone
7. Supports multiple users with role-based access control (Admin, Manager, Sales, Viewer)

## User Management & Authentication
- **Admin-controlled access**: Only administrators can create user accounts
- **No public signup**: Users cannot register themselves — prevents unauthorized access
- **Four roles available**:
  - **Admin**: Full access + user management + RBAC control
  - **Manager**: All leads + scores + reports + dashboard
  - **Sales**: Assigned leads only, no other user data
  - **Viewer**: Read-only access, no scores visible
- **Admin can**: Create users, edit roles, deactivate/activate accounts, delete users
- **Password management**: Admins set initial passwords, can reset passwords for any user

## Current Data
- 1,020 companies in database
- 21,420 scores calculated
- 21 ABBK services configured with individual scoring weights
- Real hiring signals from emploi.tn and keejob.com
- Real news signals from businessnews.com.tn

## Architecture
- Backend: FastAPI Python (port 8000)
- Frontend: React + Vite (port 5173)
- Database: PostgreSQL 16 with pgvector
- Task Queue: Celery + Redis (background scraping)
- Containers: Docker Compose (7 services)
- Scraping: Scrapy + Playwright
- AI: Claude API for signal extraction

## To Upgrade with LinkedIn Data
Add APIFY_API_TOKEN to .env file and enable the LinkedIn connector. This adds employee data, role detection, and company enrichment from LinkedIn profiles — dramatically improving score accuracy.

## Milestones Completed
- M1 Foundation: Docker, Auth, RBAC, Database — 100%
- M2 Scraping Engine: 9 spiders, enrichment, deduplication — 100%
- M3 Scoring Engine: 21 services, Claude API, notifications — 100%
- M4 Dashboard: 23 pages, mobile responsive, analytics — 100%

## Next Steps for ABBK
1. Add Apify subscription (~$50/month) for LinkedIn data
2. Deploy to Hetzner VPS (~€10/month) for permanent access
3. Connect ABBK's existing database via CSV import
4. Tune scoring weights based on manager's experience of which leads convert
5. Add email notifications when hot leads detected

## Developer Contact
Rayhane Nouri
Final-year Electrical Engineering Student
rayhane.nouri1@gmail.com
