# ABBK LeadEngine - System Architecture

**Last Updated:** July 13, 2026  
**Version:** 1.0 Production  
**Author:** Rayhane Nouri

---

## High-Level Architecture Overview

LeadEngine is a distributed system built on a microservices-inspired architecture using Docker containers. The system operates in three main layers: presentation (React SPA), application logic (FastAPI), and data persistence (PostgreSQL). Background jobs and scraping tasks run asynchronously via Celery workers.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER DEVICES                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  Desktop     │  │   Mobile     │  │    Tablet    │                 │
│  │  Browser     │  │   Browser    │  │   Browser    │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
└─────────┼──────────────────┼──────────────────┼──────────────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    HTTPS (port 443)
                             │
          ┌──────────────────▼─────────────────┐
          │   NGINX Reverse Proxy              │
          │   (SSL termination)                │
          │   nginx:alpine                     │
          │   Port: 80, 443                    │
          └──────┬─────────────────────┬───────┘
                 │                     │
        HTTP 5173│                     │HTTP 8000
                 │                     │
   ┌─────────────▼──────────┐   ┌─────▼──────────────────────┐
   │  FRONTEND               │   │  BACKEND API               │
   │  abbk_frontend          │   │  abbk_backend              │
   │  ─────────────          │   │  ─────────────             │
   │  React 18               │   │  FastAPI 0.104             │
   │  Vite 5.0               │   │  Python 3.12               │
   │  Tailwind CSS 3.4       │   │  uvicorn (ASGI)            │
   │  Framer Motion          │   │  SQLAlchemy 2.0 (async)    │
   │  Port: 5173             │   │  Pydantic v2               │
   │                         │   │  Port: 8000                │
   │  Routes:                │   │                            │
   │  /login                 │   │  Endpoints:                │
   │  /dashboard             │   │  /api/auth/login           │
   │  /leads                 │   │  /api/leads (CRUD)         │
   │  /analytics             │   │  /api/scores               │
   │  /pipeline              │   │  /api/signals              │
   └─────────────────────────┘   │  /api/analytics            │
                                 │  /health                   │
                                 └────┬──────────────┬────────┘
                                      │              │
                                      │              │JWT Auth
                                      │              │RBAC (4 roles)
                                      │              │
                       ┌──────────────▼──────────────▼───────────┐
                       │  DATABASE                               │
                       │  abbk_db                                │
                       │  ──────────                             │
                       │  PostgreSQL 16 + pgvector               │
                       │  Port: 5432 (internal)                  │
                       │                                         │
                       │  Tables:                                │
                       │  • users (auth, RBAC)                   │
                       │  • leads (companies)                    │
                       │  • lead_signals (business intel)        │
                       │  • lead_scores (21 scores per lead)     │
                       │  • services (ABBK products)             │
                       │  • lead_status_history (audit trail)    │
                       │                                         │
                       │  Indexes:                               │
                       │  • idx_leads_company_name               │
                       │  • idx_signals_lead_id                  │
                       │  • idx_scores_lead_service              │
                       └─────────────────────────────────────────┘
                                      ▲
                                      │
                                      │ Async queries
                                      │ (asyncpg driver)
                                      │
   ┌──────────────────────────────────┴────────────────────────────────┐
   │  BACKGROUND WORKERS                                               │
   │                                                                   │
   │  ┌─────────────────────────┐   ┌──────────────────────────────┐ │
   │  │ CELERY WORKER            │   │ CELERY BEAT SCHEDULER        │ │
   │  │ abbk_worker              │   │ abbk_beat                    │ │
   │  │ ───────────              │   │ ──────────                   │ │
   │  │ Concurrency: 4           │   │ Schedule:                    │ │
   │  │                          │   │ • Daily 2AM: scrape_all()    │ │
   │  │ Tasks:                   │   │ • Daily 4AM: recalc_scores() │ │
   │  │ • scrape_directories     │   │ • Weekly: cleanup_old_data() │ │
   │  │ • scrape_jobs            │   │                              │ │
   │  │ • scrape_news            │   │ Runs beat schedules          │ │
   │  │ • deep_enrich_leads      │   │ and cron-like jobs           │ │
   │  │ • calculate_scores       │   │                              │ │
   │  │ • send_notifications     │   └──────────────────────────────┘ │
   │  └───────────┬──────────────┘                                    │
   └──────────────┼───────────────────────────────────────────────────┘
                  │
                  │ Task queue
                  │ (Redis pub/sub)
                  │
   ┌──────────────▼──────────────┐
   │  MESSAGE BROKER & CACHE      │
   │  abbk_redis                  │
   │  ───────────                 │
   │  Redis 7.x (Alpine)          │
   │  Port: 6379 (internal)       │
   │                              │
   │  Usage:                      │
   │  1. Celery task queue        │
   │  2. Result backend           │
   │  3. Session cache            │
   │  4. API rate limiting        │
   │  5. Claude API response cache│
   └──────────────────────────────┘


   ┌────────────────────────────────────────────────────────────────┐
   │  MONITORING                                                    │
   │  abbk_flower                                                   │
   │  ────────────                                                  │
   │  Flower 2.0 (Celery monitoring UI)                            │
   │  Port: 5555                                                    │
   │  URL: http://localhost:5555                                    │
   │                                                                │
   │  Shows:                                                        │
   │  • Active/completed/failed tasks                              │
   │  • Worker health and performance                              │
   │  • Task execution time graphs                                 │
   │  • Celery Beat schedule                                       │
   └────────────────────────────────────────────────────────────────┘
```

---

## External Services Integration

```
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL DATA SOURCES                           │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│  WEB SCRAPING        │         │  API INTEGRATIONS    │
│  (Scrapy + Playwright)│         │                      │
│                      │         │                      │
│  Current:            │         │  Current:            │
│  • Company websites  │         │  • Claude Sonnet 4.5 │
│  • emploi.tn         │         │    (Anthropic API)   │
│  • keejob.com        │         │    Signal extraction │
│  • businessnews.tn   │         │    Text analysis     │
│  • managers.com.tn   │         │                      │
│                      │         │  Pending Approval:   │
│  Pending Approval:   │         │  • Apify LinkedIn    │
│  • LinkedIn (via     │         │    Company Scraper   │
│    Apify API)        │         │    Jobs Scraper      │
│  • Google Maps (via  │         │                      │
│    Apify API)        │         │  • Apify Google Maps │
│                      │         │    Business Scraper  │
│  Rate Limits:        │         │                      │
│  • 2-3 sec delay     │         │  Rate Limits:        │
│  • Rotating headers  │         │  • Claude: 50 req/min│
│  • Respect robots.txt│         │  • Apify: Plan-based │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                │
           │                                │
           └────────────┬───────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ CELERY WORKERS  │
              │ Process & store │
              └─────────────────┘
```

---

## Data Flow: From Scraping to Dashboard

**1. Lead Discovery Flow**

```
Start
  │
  ├─→ [Celery Beat triggers at 2AM daily]
  │
  ├─→ [Celery Worker picks up scraping task]
  │
  ├─→ [Scrapy spiders crawl target websites]
  │     • directories_spider.py → Business directories
  │     • jobs_spider.py → Job boards
  │     • news_spider.py → News sites
  │
  ├─→ [Extract company data: name, website, sector, city]
  │
  ├─→ [Deduplication check in database]
  │     SELECT * FROM leads WHERE company_name ILIKE '%...%'
  │     OR website = '...'
  │
  ├─→ [If NEW → Insert into leads table]
  │     INSERT INTO leads (company_name, website, ...)
  │
  └─→ [Trigger enrichment task]
        └─→ deep_enrich_single_lead(lead_id)
```

**2. Enrichment Flow**

```
Start (lead_id)
  │
  ├─→ [Fetch lead from database]
  │
  ├─→ [If website exists → DeepCompanyEnricher]
  │     │
  │     ├─→ Scrape homepage (Playwright/httpx)
  │     ├─→ Find key pages: /about, /careers, /products
  │     ├─→ Scrape each page (max 5KB per page)
  │     │
  │     └─→ Extract text content → enrichment_data JSON
  │
  ├─→ [Send to Claude API for signal detection]
  │     │
  │     ├─→ Prompt: "Analyze this company text. Detect:
  │     │     • Engineering team (yes/no)
  │     │     • CAD software mentions (yes/no)
  │     │     • ISO certification (yes/no)
  │     │     • Multinational presence (yes/no)
  │     │     • Export activity (yes/no)
  │     │     • Employee count (number or null)
  │     │     • Job openings (list)"
  │     │
  │     └─→ Claude returns structured JSON response
  │           (cached in DB to avoid re-calling same text)
  │
  ├─→ [Update lead.scraped_data = enrichment_data]
  │
  ├─→ [Update flags: is_multinational, is_exporter, under_audit]
  │
  ├─→ [Create LeadSignal records for each detected signal]
  │     INSERT INTO lead_signals (lead_id, signal_type, title, 
  │                                detail, source_url, detected_at)
  │
  └─→ [Trigger scoring task]
        └─→ calculate_lead_score(lead_id)
```

**3. Scoring Flow**

```
Start (lead_id)
  │
  ├─→ [Fetch lead from database]
  │
  ├─→ [Fetch all signals for this lead]
  │     SELECT * FROM lead_signals WHERE lead_id = ?
  │
  ├─→ [Map signals to scoring keys]
  │     {
  │       'new_hire': 2 signals found,
  │       'is_multinational': True,
  │       'is_exporter': True,
  │       'under_audit': True,
  │       'role_detected': 1 signal,
  │       'logo_detected': 1 signal
  │     }
  │
  ├─→ [Fetch all active services (21 ABBK products)]
  │     SELECT * FROM services WHERE is_active = true
  │
  ├─→ [For EACH service, calculate score]
  │     │
  │     ├─→ Get service.scoring_weights
  │     │     Example for SOLIDWORKS Simulation:
  │     │     {
  │     │       'role_detected': 40,
  │     │       'logo_detected': 30,
  │     │       'is_multinational': 15,
  │     │       'under_audit': 10,
  │     │       'new_hire': 5
  │     │     }
  │     │     Total possible: 100
  │     │
  │     ├─→ Sum weights for detected signals
  │     │     role_detected (40) + logo_detected (30) + 
  │     │     is_multinational (15) + under_audit (10) = 95
  │     │
  │     ├─→ Normalize to 0-100
  │     │     score = (95 / 100) * 100 = 95
  │     │
  │     ├─→ Generate reasoning text
  │     │     "HOT LEAD - Score: 95/100 for SOLIDWORKS Simulation.
  │     │      Signals: Engineering team detected (40pts), CAD 
  │     │      software found (30pts), Multinational (15pts), 
  │     │      ISO certified (10pts). Recommendation: Lead with 
  │     │      Simulation + Training package."
  │     │
  │     └─→ UPSERT into lead_scores table
  │           INSERT INTO lead_scores (lead_id, service_name, 
  │                                     score, reasoning, scored_at)
  │           ON CONFLICT (lead_id, service_name) DO UPDATE
  │
  └─→ [All 21 scores calculated]
        └─→ Dashboard can now display ranked leads
```

**4. User Access Flow**

```
User opens browser
  │
  ├─→ Loads React app from http://localhost:5173
  │
  ├─→ Sees /login page
  │
  ├─→ Enters email + password
  │
  ├─→ POST /api/auth/login
  │     │
  │     ├─→ FastAPI validates credentials (bcrypt password hash)
  │     ├─→ If valid → Generate JWT token (expires 7 days)
  │     ├─→ Return: { access_token: "eyJ...", user: {...} }
  │
  ├─→ Frontend stores token in localStorage
  │
  ├─→ Redirect to /dashboard
  │
  ├─→ GET /api/leads?skip=0&limit=50
  │     Headers: { Authorization: "Bearer eyJ..." }
  │     │
  │     ├─→ FastAPI validates JWT
  │     ├─→ Check user role (RBAC: admin/manager/sales/viewer)
  │     ├─→ Query database with filters
  │     ├─→ Return: { leads: [...], total: 15, has_more: false }
  │
  ├─→ Dashboard renders metrics and lead cards
  │
  └─→ User clicks on ACTIA → Navigate to /leads/2
        │
        └─→ GET /api/leads/2
              GET /api/signals/2
              GET /api/scores/2
              │
              └─→ Company profile page renders with:
                    • Company info
                    • 6 signals with source URLs
                    • 21 score cards
                    • Recommendation text
```

---

## Technology Stack Justification

### Frontend: React 18 + Vite
**Why?**
- Vite: 10x faster dev server than Create React App (HMR in <100ms)
- React: Industry standard, large ecosystem
- Tailwind: Rapid UI development without CSS bloat
- Framer Motion: Smooth animations for professional feel

**Alternatives considered:**
- ❌ Vue.js - smaller ecosystem, less ABBK dev familiarity
- ❌ Next.js - overkill for SPA, no SSR needed here
- ❌ Angular - too heavy, steeper learning curve

### Backend: FastAPI
**Why?**
- Async by default → handles concurrent requests efficiently
- Auto-generated OpenAPI docs (Swagger UI at /docs)
- Pydantic validation → catches bad data at API boundary
- Type hints → better IDE support and fewer runtime errors
- 3x faster than Flask/Django for I/O-bound tasks

**Alternatives considered:**
- ❌ Django - synchronous, slower for async scraping tasks
- ❌ Flask - no native async, no auto validation
- ❌ Express.js - would require rewriting scoring logic in JS

### Database: PostgreSQL 16
**Why?**
- ACID transactions → data integrity for lead updates
- JSON columns → flexible storage for scraped_data
- pgvector extension → future: semantic search on company descriptions
- Mature, battle-tested, free
- Async driver (asyncpg) integrates with FastAPI

**Alternatives considered:**
- ❌ MySQL - weaker JSON support, no pgvector
- ❌ MongoDB - no ACID transactions, harder to maintain relationships
- ❌ SQLite - not suitable for production concurrent writes

### Task Queue: Celery + Redis
**Why?**
- Celery: battle-tested async task queue (10+ years, massive community)
- Redis: in-memory broker → fast task dispatch
- Celery Beat: built-in cron scheduler (no need for external cron)
- Flower: excellent monitoring UI out-of-the-box

**Alternatives considered:**
- ❌ RQ (Redis Queue) - simpler but no Beat scheduler
- ❌ Kafka - overkill for this scale, harder to operate
- ❌ Cron + custom scripts - no task monitoring, no retries, no failure handling

### Scraping: Scrapy + Playwright
**Why?**
- Scrapy: high-performance for static sites (50+ pages/min)
- Playwright: handles JavaScript-heavy sites (LinkedIn, modern SPAs)
- Both: mature, well-documented, large communities

**Alternatives considered:**
- ❌ BeautifulSoup - no concurrency, manual request handling
- ❌ Selenium - slower than Playwright, heavier resource usage
- ❌ Puppeteer - NodeJS only, would require separate service

### AI: Claude Sonnet 4.5 (Anthropic API)
**Why?**
- Best at structured extraction (signals from unstructured text)
- JSON mode → reliable parsing
- Prompt caching → 90% cost reduction on repeated text
- 200K context → can analyze entire website in one call

**Alternatives considered:**
- ❌ GPT-4 - more expensive, less reliable JSON output
- ❌ Local LLM (Llama) - requires GPU, slower, less accurate
- ❌ Rule-based extraction - brittle, misses nuanced signals

---

## Deployment Architecture (Production)

```
                        Internet
                           │
                           │ DNS: leadengine.abbk-tn.com
                           ▼
                   ┌───────────────┐
                   │  Cloudflare   │
                   │  (optional)   │
                   │  CDN + DDoS   │
                   └───────┬───────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  Hetzner VPS CX31    │
                │  ─────────────────   │
                │  4 vCPU, 8GB RAM     │
                │  160GB SSD           │
                │  Ubuntu 24.04 LTS    │
                │  Location: Germany   │
                │  €12.50/month        │
                └──────────┬───────────┘
                           │
                ┌──────────▼────────────────────────────────────┐
                │  Host OS: Ubuntu 24.04                        │
                │  ───────────────────────                      │
                │  • Docker 24.x                                │
                │  • Docker Compose v2                          │
                │  • UFW Firewall (ports 80, 443, 22 only)      │
                │  • Fail2ban (SSH brute-force protection)      │
                │  • Let's Encrypt SSL (auto-renew)             │
                └───────────────────────────────────────────────┘
                           │
                           │ docker-compose.yml
                           │ defines 7 services
                           ▼
        ┌──────────────────────────────────────────────────┐
        │  Docker Network: abbk_network (bridge mode)     │
        │  ─────────────────────────────────────────────   │
        │                                                  │
        │  abbk_nginx    : 80, 443 → exposed              │
        │  abbk_frontend : 5173 → internal only           │
        │  abbk_backend  : 8000 → internal only           │
        │  abbk_db       : 5432 → internal only           │
        │  abbk_redis    : 6379 → internal only           │
        │  abbk_worker   : no ports                       │
        │  abbk_beat     : no ports                       │
        │  abbk_flower   : 5555 → internal (VPN only)     │
        │                                                  │
        │  Volumes (persistent data):                     │
        │  • postgres_data → /var/lib/postgresql/data     │
        │  • redis_data → /data                           │
        │  • nginx_ssl → /etc/letsencrypt                 │
        └──────────────────────────────────────────────────┘
```

**Backup Strategy:**
- Database: Daily automated backup to Hetzner Storage Box (€3.20/month for 100GB)
- Retention: 7 daily, 4 weekly, 3 monthly
- Backup script: `scripts/backup_db.sh` (runs via cron)
- Recovery tested: Yes (restore time: ~5 minutes for 1GB database)

**Monitoring:**
- Uptime: UptimeRobot (free tier, 5-min checks)
- Logs: Docker logs rotated daily, kept for 30 days
- Alerts: Email on service down, disk >80%, DB connection failures

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  SECURITY LAYERS                                            │
└─────────────────────────────────────────────────────────────┘

Layer 1: Network
  • UFW firewall: Allow only 80, 443, 22
  • SSH: Key-based auth only, password auth disabled
  • Fail2ban: 5 failed SSH attempts → 10 min IP ban
  • Docker internal network: Services isolated from host

Layer 2: Transport
  • SSL/TLS 1.3 via Let's Encrypt
  • HSTS headers (force HTTPS)
  • Nginx rate limiting: 10 req/sec per IP

Layer 3: Authentication
  • JWT tokens (HS256 algorithm)
  • Secret key: 256-bit random (from env var)
  • Token expiry: 7 days
  • Refresh token: Not implemented (future enhancement)

Layer 4: Authorization (RBAC)
  • 4 roles: admin, manager, sales, viewer
  • Enforced at API route level (FastAPI dependencies)
  • admin: Full access + user management
  • manager: All leads, all scores, reports
  • sales: Assigned leads only, no other users' data
  • viewer: Read-only, no scores visible

Layer 5: Data Protection
  • Passwords: bcrypt (cost factor 12)
  • Database: No public exposure, Docker internal network only
  • Secrets: .env file (never committed to git)
  • API keys: Environment variables, not hardcoded
  • Scraped data: No PII collected (company data only, no personal emails/phones)

Layer 6: Input Validation
  • Pydantic schemas validate all API requests
  • SQL injection: Protected by SQLAlchemy ORM (parameterized queries)
  • XSS: React escapes all user input by default
  • CORS: Restricted to frontend origin only
```

---

## Scalability Considerations

**Current Capacity (Hetzner CX31):**
- Leads: Up to 100,000 companies
- Concurrent users: 20-30
- API requests: 100 req/sec
- Scraping throughput: 50 companies/hour

**Bottlenecks Identified:**
1. **Database** - Single PostgreSQL instance
   - **Solution:** Add read replica when >10,000 leads
   
2. **Celery Workers** - Single worker, 4 threads
   - **Solution:** Horizontal scaling → spawn 2-3 worker containers
   
3. **Claude API** - Rate limit 50 req/min
   - **Solution:** Batch text analysis, aggressive caching
   
4. **Apify** - Plan-based limits (e.g., 10K actors/month on Starter)
   - **Solution:** Upgrade to Team plan ($249/month) for 100K actors

**Scaling Path (0 → 100K companies):**

| Leads | Users | Server      | Monthly Cost | Changes Needed |
|-------|-------|-------------|--------------|----------------|
| 0-5K  | <10   | CX31        | €12.50       | None (current) |
| 5-20K | 10-30 | CX41        | €25          | +4 vCPU, +8GB RAM |
| 20-50K| 30-50 | CX51        | €50          | +8 vCPU, +16GB RAM, DB replica |
| 50-100K| 50-100| CPX51       | €100         | +16 vCPU, +32GB RAM, 2 workers |
| 100K+ | 100+  | Managed Infra| €500+       | Kubernetes, managed DB |

**Horizontal Scaling Strategy (future):**
- Load balancer (Nginx or HAProxy)
- 3 backend instances behind LB
- Managed PostgreSQL (Hetzner or DigitalOcean)
- Separate Celery worker fleet (auto-scale based on queue depth)
- Redis cluster (3 nodes for HA)

---

## Performance Benchmarks

**API Response Times (average, p95, p99):**

| Endpoint | Avg | p95 | p99 | Notes |
|----------|-----|-----|-----|-------|
| GET /api/leads?limit=50 | 120ms | 250ms | 400ms | Includes 50 leads + scores |
| GET /api/leads/{id} | 80ms | 150ms | 200ms | Single lead |
| GET /api/scores/{lead_id} | 60ms | 100ms | 150ms | 21 scores |
| POST /api/auth/login | 350ms | 500ms | 650ms | Bcrypt hashing is slow by design |
| GET /api/analytics/overview | 200ms | 400ms | 600ms | Aggregates across all leads |

**Database Query Performance:**

| Query | Time | Notes |
|-------|------|-------|
| SELECT * FROM leads LIMIT 50 | 15ms | Indexed on created_at |
| Lead scores for 1 company | 8ms | Indexed on (lead_id, service_name) |
| All signals for 1 company | 5ms | Indexed on lead_id |
| Calculate scores for 1 lead | 2.5s | Calls Claude API (network latency) |
| Scrape 1 company website | 8-15s | Depends on website size and latency |

**Scraping Throughput:**

| Spider | Pages/Hour | Leads/Hour | Notes |
|--------|------------|------------|-------|
| directories_spider | 100 | 30-50 | Static HTML, fast |
| jobs_spider | 50 | 10-20 | Pagination, slower |
| deep_enrichment | 20-30 | 20-30 | Visits 4-5 pages per company |
| LinkedIn (via Apify) | N/A | 500+ | Parallel scraping, fast |

---

## Failure Modes & Recovery

**What happens if...**

| Failure Scenario | Impact | Auto-Recovery | Manual Recovery |
|------------------|--------|---------------|-----------------|
| Backend crashes | Frontend shows errors | Docker restart policy | `docker compose restart backend` |
| Database crashes | Entire system down | Docker restart | Restore from backup |
| Redis crashes | Celery tasks fail | Docker restart | Clear queue, restart workers |
| Celery worker dies | Scraping stops | None | `docker compose restart worker` |
| Disk full | All writes fail | None | Clear logs, expand disk |
| Claude API down | Scoring fails | Celery retry (3x) | Wait for Anthropic recovery |
| SSL cert expires | HTTPS fails | Let's Encrypt auto-renew | `certbot renew --force-renewal` |
| Scraped site blocks us | That spider fails | Skip and continue | Add proxy, change user agent |

**Recovery Time Objectives (RTO):**
- Critical (DB crash): 15 minutes
- High (backend crash): 2 minutes (auto-restart)
- Medium (worker crash): 5 minutes
- Low (scraper fails): Next scheduled run

**Recovery Point Objectives (RPO):**
- Database: 24 hours (daily backups)
- Scraped data: 24 hours (re-scrape if needed)
- User sessions: 0 (stored in Redis, ephemeral)

---

## Development vs Production Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| Domain | localhost:5173 | leadengine.abbk-tn.com |
| HTTPS | No | Yes (Let's Encrypt) |
| Database | Docker PostgreSQL | Docker PostgreSQL (same) |
| Secrets | .env file | .env file (different values) |
| Logs | stdout | stdout + file rotation |
| Debug mode | ON | OFF |
| CORS | Allow all | Restrict to domain |
| Backup | None | Daily automated |
| Monitoring | None | UptimeRobot + logs |
| Hot reload | Yes (Vite HMR) | No |
| Docker restart | no (manual) | always |

---

## API Rate Limits

**Inbound (API requests TO our backend):**
- Rate limit: 100 requests/minute per IP (Nginx)
- Burst: 20 requests
- Penalty: HTTP 429 Too Many Requests

**Outbound (API requests FROM our backend):**

| Service | Limit | Our Usage | Risk |
|---------|-------|-----------|------|
| Claude API | 50 req/min | 5-10 req/min | Low |
| Apify (pending) | Plan-based | 20-30 req/day | Low |
| Target websites | Polite (2-3s delay) | 10-20 req/hour/site | Low |

**If rate limit hit:**
- Claude API: Celery task retries with exponential backoff (1s, 2s, 4s)
- Scraped sites: Sleep 60s, then retry (max 3 attempts)
- Apify: Queue requests, process sequentially

---

## Maintenance Windows

**Scheduled Maintenance:**
- Database backups: Daily 3:00 AM Tunisia time (non-disruptive, read-only lock for 30s)
- Scraping tasks: Daily 2:00 AM (background, no user impact)
- Score recalculation: Daily 4:00 AM (background, no user impact)
- Log rotation: Daily 5:00 AM (non-disruptive)
- Docker image updates: Monthly, Sunday 2:00 AM (5-10 min downtime)

**Deployment Updates:**
- Frequency: As needed (bug fixes, new features)
- Process: Blue-green deployment (zero downtime)
- Rollback time: <2 minutes if deployment fails

---

## Dependencies & Versions

**Backend:**
- Python: 3.12.x
- FastAPI: 0.104.x
- SQLAlchemy: 2.0.x
- Celery: 5.3.x
- Scrapy: 2.11.x
- Playwright: 1.40.x
- httpx: 0.25.x (async HTTP)
- Anthropic SDK: 0.40.x

**Frontend:**
- Node: 20.x LTS
- React: 18.2.x
- Vite: 5.0.x
- Tailwind: 3.4.x
- Framer Motion: 10.x

**Infrastructure:**
- PostgreSQL: 16.x
- Redis: 7.x
- Docker: 24.x
- Docker Compose: 2.x
- Nginx: latest (alpine)

**Last updated:** July 13, 2026

---

## Future Enhancements (Post-v1.0)

**Planned for v1.1 (Q3 2026):**
- ✅ Apify LinkedIn integration (pending approval)
- ✅ Apify Google Maps integration (pending approval)
- Real-time job scraping (daily updates)
- Email notifications for hot leads
- Export to CSV/Excel

**Planned for v2.0 (Q4 2026):**
- Mobile app (React Native)
- CRM integration (Salesforce, HubSpot)
- WhatsApp integration for sales team
- Expand to Algeria and Morocco
- Multi-language support (French/Arabic UI)

---

**Document Version:** 1.0  
**Last Reviewed:** July 13, 2026  
**Next Review:** August 13, 2026
