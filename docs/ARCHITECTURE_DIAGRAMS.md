# ABBK LeadEngine - Architecture Diagrams

**View these diagrams:**
- GitHub/GitLab: Renders automatically in markdown
- VS Code: Install "Markdown Preview Mermaid Support" extension
- Online: Copy diagram code to https://mermaid.live
- Export: Use mermaid.live to export as PNG/SVG/PDF

---

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "User Layer"
        USER[👤 Sales Manager<br/>Desktop/Mobile Browser]
    end

    subgraph "Presentation Layer - Port 5173"
        FRONTEND[React 18 Frontend<br/>abbk_frontend<br/>Vite + Tailwind CSS]
    end

    subgraph "Application Layer - Port 8000"
        API[FastAPI Backend<br/>abbk_backend<br/>Python 3.12 + uvicorn]
        AUTH[JWT Authentication<br/>RBAC Middleware]
    end

    subgraph "Background Processing"
        WORKER[Celery Worker<br/>abbk_worker<br/>4 concurrent threads]
        BEAT[Celery Beat<br/>abbk_beat<br/>Cron Scheduler]
        FLOWER[Flower UI<br/>abbk_flower<br/>Port 5555]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL 16<br/>abbk_db<br/>Port 5432)]
        REDIS[(Redis 7<br/>abbk_redis<br/>Port 6379)]
    end

    subgraph "External Services"
        CLAUDE[Claude API<br/>Sonnet 4.5<br/>Signal Extraction]
        APIFY[Apify API<br/>LinkedIn + Google Maps<br/>Premium Scraping]
        WEB[Web Scraping<br/>Scrapy + Playwright<br/>Company Websites]
    end

    USER -->|HTTPS| FRONTEND
    FRONTEND -->|REST API| API
    API -->|Validate| AUTH
    AUTH -->|Query| DB
    API -->|Cache/Sessions| REDIS
    API -->|Queue Tasks| REDIS
    
    WORKER -->|Consume Tasks| REDIS
    WORKER -->|Store Results| DB
    WORKER -->|Call| CLAUDE
    WORKER -->|Call| APIFY
    WORKER -->|Scrape| WEB
    
    BEAT -->|Schedule Tasks| REDIS
    BEAT -.->|Monitor| FLOWER
    WORKER -.->|Monitor| FLOWER

    style USER fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style FRONTEND fill:#61DAFB,stroke:#21A1C4,color:#000
    style API fill:#009688,stroke:#00695C,color:#fff
    style DB fill:#336791,stroke:#23527C,color:#fff
    style REDIS fill:#DC382D,stroke:#A62C24,color:#fff
    style CLAUDE fill:#D4A574,stroke:#8B6F47,color:#000
    style APIFY fill:#6C5CE7,stroke:#5849C4,color:#fff
```

---

## 2. Database Schema (ER Diagram)

```mermaid
erDiagram
    USERS ||--o{ LEADS : "assigned_to"
    LEADS ||--o{ LEAD_SIGNALS : "has_many"
    LEADS ||--o{ LEAD_SCORES : "has_many"
    SERVICES ||--o{ LEAD_SCORES : "scored_by"
    LEADS ||--o{ LEAD_STATUS_HISTORY : "tracks"

    USERS {
        uuid id PK
        string email UK
        string full_name
        string hashed_password
        enum role "admin/manager/sales/viewer"
        boolean is_active
        json permissions
        timestamp created_at
        timestamp updated_at
    }

    LEADS {
        int id PK
        string company_name
        string website UK
        string linkedin_url
        string country
        string city
        string sector
        int employee_count
        boolean is_multinational
        boolean is_exporter
        boolean under_audit
        json scraped_data "Raw HTML/JSON from all sources"
        enum status "new/qualified/contacted/converted/lost"
        timestamp created_at
        timestamp updated_at
        uuid assigned_to FK
    }

    LEAD_SIGNALS {
        int id PK
        int lead_id FK
        string signal_type "new_hire/role_detected/training/etc"
        string title
        text detail
        string source_url
        timestamp detected_at
    }

    LEAD_SCORES {
        int id PK
        int lead_id FK
        int service_id FK
        string service_type "software/training"
        string service_name "SOLIDWORKS/Simulation/etc"
        float score "0-100"
        text reasoning "AI-generated explanation"
        json signal_breakdown "Which signals fired + weights"
        timestamp scored_at
    }

    SERVICES {
        int id PK
        string name UK
        enum service_type "software/training"
        text description
        json scoring_weights "Signal to weight mapping"
        boolean is_active
        timestamp created_at
    }

    LEAD_STATUS_HISTORY {
        int id PK
        int lead_id FK
        enum old_status
        enum new_status
        uuid changed_by FK
        text notes
        timestamp changed_at
    }
```

---

## 3. Data Flow - Lead Discovery to Scoring

```mermaid
flowchart TD
    START([Celery Beat Trigger<br/>Daily 2:00 AM]) --> SCRAPE_TASK[Queue Scraping Tasks]
    
    SCRAPE_TASK --> DIR[Directories Spider<br/>annuaire.tn, pagesjaunes.tn]
    SCRAPE_TASK --> JOBS[Jobs Spider<br/>emploi.tn, keejob.com]
    SCRAPE_TASK --> NEWS[News Spider<br/>businessnews.tn]
    
    DIR --> EXTRACT[Extract Company Data<br/>name, website, sector, city]
    JOBS --> EXTRACT
    NEWS --> EXTRACT
    
    EXTRACT --> DEDUP{Duplicate<br/>Check}
    DEDUP -->|Exists| SKIP[Skip - Already in DB]
    DEDUP -->|New| INSERT[Insert into leads table]
    
    INSERT --> ENRICH_TASK[Queue Enrichment Task<br/>deep_enrich_lead]
    
    ENRICH_TASK --> FETCH_WEB[Scrape Company Website<br/>Playwright + httpx]
    FETCH_WEB --> PAGES[Extract Key Pages<br/>/about /careers /products]
    
    PAGES --> CLAUDE_API[Call Claude API<br/>Extract Signals]
    CLAUDE_API --> SIGNALS[Detected Signals:<br/>✓ Engineering team<br/>✓ ISO certification<br/>✓ Multinational<br/>✓ Job openings]
    
    SIGNALS --> UPDATE_DB[Update Database]
    UPDATE_DB --> SAVE_RAW[Save scraped_data JSON]
    UPDATE_DB --> SAVE_FLAGS[Set flags: is_multinational,<br/>is_exporter, under_audit]
    UPDATE_DB --> SAVE_SIGNALS[Create LeadSignal records]
    
    SAVE_SIGNALS --> SCORE_TASK[Queue Scoring Task<br/>calculate_scores]
    
    SCORE_TASK --> GET_SERVICES[Fetch 21 ABBK Services]
    GET_SERVICES --> CALC_LOOP[For Each Service]
    
    CALC_LOOP --> MAP_SIGNALS[Map Signals to Weights<br/>Example: role_detected=40pts]
    MAP_SIGNALS --> SUM_SCORE[Sum Fired Signal Weights<br/>Normalize to 0-100]
    SUM_SCORE --> REASONING[Generate Reasoning Text<br/>via Claude API]
    REASONING --> SAVE_SCORE[Upsert lead_scores table]
    
    SAVE_SCORE --> DONE{More<br/>Services?}
    DONE -->|Yes| CALC_LOOP
    DONE -->|No| FINISH([Lead Ready for Dashboard])
    
    style START fill:#4CAF50,stroke:#2E7D32,color:#fff
    style CLAUDE_API fill:#D4A574,stroke:#8B6F47,color:#000
    style FINISH fill:#2196F3,stroke:#1565C0,color:#fff
    style DEDUP fill:#FF9800,stroke:#E65100,color:#fff
    style INSERT fill:#9C27B0,stroke:#6A1B9A,color:#fff
```

---

## 4. API Request Flow with Authentication

```mermaid
sequenceDiagram
    actor User as Sales Manager
    participant Browser as React Frontend
    participant API as FastAPI Backend
    participant Auth as JWT Middleware
    participant DB as PostgreSQL
    participant Redis as Redis Cache

    User->>Browser: Enter email + password
    Browser->>API: POST /api/auth/login<br/>{email, password}
    API->>DB: SELECT user WHERE email=?
    DB-->>API: User record + hashed_password
    API->>API: bcrypt.verify(password, hash)
    API->>API: Generate JWT token<br/>(expires 7 days)
    API-->>Browser: {access_token, user}
    Browser->>Browser: Store token in localStorage
    
    Note over User,Redis: User navigates to Dashboard
    
    Browser->>API: GET /api/leads?limit=50<br/>Authorization: Bearer eyJ...
    API->>Auth: Validate JWT signature
    Auth->>Auth: Decode payload<br/>{user_id, role, exp}
    Auth->>Auth: Check expiration
    Auth->>Redis: Check token blacklist
    Redis-->>Auth: Token valid
    Auth->>DB: SELECT user WHERE id=user_id
    DB-->>Auth: User record
    Auth->>Auth: Check role permissions<br/>(RBAC: manager can view all)
    Auth-->>API: ✓ Authorized
    
    API->>DB: SELECT leads<br/>ORDER BY created_at DESC<br/>LIMIT 50
    DB-->>API: 50 lead records
    
    loop For each lead
        API->>DB: SELECT lead_scores<br/>WHERE lead_id=?<br/>ORDER BY score DESC
        DB-->>API: Scores for this lead
    end
    
    API-->>Browser: {leads: [...], total: 15}
    Browser->>Browser: Render dashboard cards
    Browser-->>User: Display ranked leads
```

---

## 5. Scraping and Enrichment Pipeline

```mermaid
graph LR
    subgraph "Data Sources"
        D1[Business Directories<br/>annuaire.tn<br/>pagesjaunes.tn]
        D2[Job Boards<br/>emploi.tn<br/>keejob.com]
        D3[News Sites<br/>businessnews.tn<br/>managers.tn]
        D4[LinkedIn API<br/>via Apify<br/>PENDING]
        D5[Google Maps API<br/>via Apify<br/>PENDING]
    end

    subgraph "Scraping Layer"
        S1[Scrapy Spider<br/>Static HTML]
        S2[Playwright<br/>JS-heavy sites]
        S3[Apify Actors<br/>LinkedIn + Maps]
    end

    subgraph "Processing"
        P1[Deduplication<br/>by name or website]
        P2[Deep Enrichment<br/>Visit 4-5 pages per site]
        P3[Claude API<br/>Signal Extraction]
    end

    subgraph "Storage"
        DB1[(Raw Data<br/>scraped_data JSON)]
        DB2[(Structured Signals<br/>lead_signals table)]
        DB3[(Company Flags<br/>boolean fields)]
    end

    D1 --> S1
    D2 --> S1
    D3 --> S1
    D4 --> S3
    D5 --> S3
    
    S1 --> P1
    S2 --> P1
    S3 --> P1
    
    P1 --> P2
    P2 --> P3
    
    P3 --> DB1
    P3 --> DB2
    P3 --> DB3

    style D4 fill:#FFF59D,stroke:#F9A825,color:#000
    style D5 fill:#FFF59D,stroke:#F9A825,color:#000
    style S3 fill:#FFF59D,stroke:#F9A825,color:#000
```

---

## 6. Scoring Engine Architecture

```mermaid
flowchart TD
    START[Lead Enrichment Complete] --> FETCH[Fetch Lead + All Signals]
    
    FETCH --> SERVICES[Load 21 ABBK Services]
    
    SERVICES --> LOOP_START{For Each Service}
    
    LOOP_START -->|SOLIDWORKS Standard| SW1[Scoring Weights:<br/>role_detected: 35pts<br/>logo_detected: 25pts<br/>new_hire: 20pts<br/>is_multinational: 15pts<br/>under_audit: 5pts]
    
    LOOP_START -->|SOLIDWORKS Simulation| SW2[Scoring Weights:<br/>role_detected: 40pts<br/>logo_detected: 30pts<br/>is_multinational: 15pts<br/>under_audit: 10pts<br/>new_hire: 5pts]
    
    LOOP_START -->|SOLIDWORKS Electrical| SW3[Scoring Weights:<br/>role_electrical: 40pts<br/>logo_detected: 30pts<br/>new_hire: 15pts<br/>is_multinational: 10pts<br/>under_audit: 5pts]
    
    SW1 --> MAP1[Map Detected Signals<br/>to Weights]
    SW2 --> MAP1
    SW3 --> MAP1
    
    MAP1 --> SUM[Sum Weights<br/>Example: 35+25+15 = 75pts]
    
    SUM --> NORMALIZE[Normalize to 0-100<br/>Score = 75/100 * 100 = 75]
    
    NORMALIZE --> CLASSIFY{Classify Score}
    
    CLASSIFY -->|70-100| HOT[🔥 HOT LEAD<br/>Call Today]
    CLASSIFY -->|60-69| WARM[🔶 WARM<br/>Call This Week]
    CLASSIFY -->|30-59| POTENTIAL[📋 POTENTIAL<br/>Add to Pipeline]
    CLASSIFY -->|0-29| RESEARCH[🔍 RESEARCH<br/>Gather More Data]
    
    HOT --> REASONING[Generate Reasoning Text<br/>via Claude API]
    WARM --> REASONING
    POTENTIAL --> REASONING
    RESEARCH --> REASONING
    
    REASONING --> SAVE[Save to lead_scores<br/>UPSERT by (lead_id, service_name)]
    
    SAVE --> LOOP_END{More Services?}
    LOOP_END -->|Yes| LOOP_START
    LOOP_END -->|No| DASHBOARD[Lead Appears in Dashboard<br/>Ranked by Best Score]
    
    style HOT fill:#F44336,stroke:#C62828,color:#fff
    style WARM fill:#FF9800,stroke:#E65100,color:#fff
    style POTENTIAL fill:#2196F3,stroke:#1565C0,color:#fff
    style RESEARCH fill:#9E9E9E,stroke:#616161,color:#fff
    style DASHBOARD fill:#4CAF50,stroke:#2E7D32,color:#fff
```

---

## 7. Production Deployment Architecture

```mermaid
graph TB
    subgraph "Internet"
        USERS[👥 ABBK Sales Team<br/>Desktop + Mobile Browsers]
        DNS[DNS: leadengine.abbk-tn.com]
    end

    subgraph "Hetzner VPS CX31 - Germany"
        subgraph "Ubuntu 24.04 LTS Host"
            FIREWALL[UFW Firewall<br/>Ports: 80, 443, 22]
            SSL[Let's Encrypt<br/>SSL Auto-Renewal]
            NGINX[Nginx Reverse Proxy<br/>Rate Limit: 100 req/min]
        end

        subgraph "Docker Network: abbk_network"
            FRONTEND_PROD[abbk_frontend<br/>React Production Build<br/>Port 5173 internal]
            BACKEND_PROD[abbk_backend<br/>FastAPI + uvicorn<br/>Port 8000 internal]
            DB_PROD[(abbk_db<br/>PostgreSQL 16<br/>Port 5432 internal)]
            REDIS_PROD[(abbk_redis<br/>Redis 7<br/>Port 6379 internal)]
            WORKER_PROD[abbk_worker<br/>Celery Worker<br/>4 threads]
            BEAT_PROD[abbk_beat<br/>Celery Beat Scheduler]
            FLOWER_PROD[abbk_flower<br/>Monitoring UI<br/>Port 5555 VPN only]
        end

        subgraph "Persistent Storage"
            VOL1[Docker Volume<br/>postgres_data]
            VOL2[Docker Volume<br/>redis_data]
        end
    end

    subgraph "External Services"
        CLAUDE_PROD[Claude API<br/>Anthropic]
        APIFY_PROD[Apify API<br/>LinkedIn + Maps]
        BACKUP[Hetzner Storage Box<br/>Daily Backups<br/>100GB]
    end

    subgraph "Monitoring"
        UPTIME[UptimeRobot<br/>5-min Health Checks]
        LOGS[Docker Logs<br/>30-day Rotation]
    end

    USERS --> DNS
    DNS --> FIREWALL
    FIREWALL --> SSL
    SSL --> NGINX
    
    NGINX -->|/:5173| FRONTEND_PROD
    NGINX -->|/api:8000| BACKEND_PROD
    
    BACKEND_PROD --> DB_PROD
    BACKEND_PROD --> REDIS_PROD
    WORKER_PROD --> DB_PROD
    WORKER_PROD --> REDIS_PROD
    BEAT_PROD --> REDIS_PROD
    
    DB_PROD -.-> VOL1
    REDIS_PROD -.-> VOL2
    
    WORKER_PROD --> CLAUDE_PROD
    WORKER_PROD --> APIFY_PROD
    
    DB_PROD -.->|Daily 3AM| BACKUP
    
    NGINX -.-> UPTIME
    BACKEND_PROD -.-> LOGS
    WORKER_PROD -.-> FLOWER_PROD

    style USERS fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style NGINX fill:#009639,stroke:#006B29,color:#fff
    style FIREWALL fill:#F44336,stroke:#C62828,color:#fff
    style BACKUP fill:#FF9800,stroke:#E65100,color:#fff
    style UPTIME fill:#4CAF50,stroke:#2E7D32,color:#fff
```

---

## 8. Celery Task Queue Architecture

```mermaid
graph LR
    subgraph "Task Producers"
        API[FastAPI Routes<br/>Manual triggers]
        BEAT[Celery Beat<br/>Cron schedules]
        USER[Admin Dashboard<br/>One-click scraping]
    end

    subgraph "Message Broker"
        REDIS[Redis<br/>Task Queue<br/>Port 6379]
    end

    subgraph "Task Consumers"
        W1[Worker Thread 1]
        W2[Worker Thread 2]
        W3[Worker Thread 3]
        W4[Worker Thread 4]
    end

    subgraph "Task Types"
        T1[scrape_directories<br/>Priority: 5]
        T2[scrape_jobs<br/>Priority: 5]
        T3[scrape_news<br/>Priority: 5]
        T4[deep_enrich_lead<br/>Priority: 8]
        T5[calculate_scores<br/>Priority: 10]
        T6[send_notifications<br/>Priority: 3]
    end

    subgraph "Result Backend"
        REDIS_RESULT[(Redis<br/>Task Results<br/>TTL: 24h)]
    end

    subgraph "Monitoring"
        FLOWER_MON[Flower UI<br/>localhost:5555]
    end

    API --> REDIS
    BEAT --> REDIS
    USER --> REDIS

    REDIS -->|Pop task| W1
    REDIS -->|Pop task| W2
    REDIS -->|Pop task| W3
    REDIS -->|Pop task| W4

    W1 --> T1
    W1 --> T4
    W2 --> T2
    W2 --> T5
    W3 --> T3
    W4 --> T6

    T1 --> REDIS_RESULT
    T2 --> REDIS_RESULT
    T3 --> REDIS_RESULT
    T4 --> REDIS_RESULT
    T5 --> REDIS_RESULT
    T6 --> REDIS_RESULT

    REDIS -.-> FLOWER_MON
    W1 -.-> FLOWER_MON
    W2 -.-> FLOWER_MON
    W3 -.-> FLOWER_MON
    W4 -.-> FLOWER_MON

    style T5 fill:#F44336,stroke:#C62828,color:#fff
    style T4 fill:#FF9800,stroke:#E65100,color:#fff
    style T1 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style FLOWER_MON fill:#9C27B0,stroke:#6A1B9A,color:#fff
```

---

## 9. RBAC (Role-Based Access Control)

```mermaid
flowchart TD
    START[User Login] --> AUTH{JWT Valid?}
    AUTH -->|No| REJECT[❌ 401 Unauthorized]
    AUTH -->|Yes| DECODE[Decode JWT Payload<br/>{user_id, role, exp}]
    
    DECODE --> CHECK_ROLE{Check Role}
    
    CHECK_ROLE -->|admin| ADMIN_PERMS[✅ Full Access<br/>+ User Management<br/>+ RBAC Control<br/>+ All Leads<br/>+ All Scores]
    
    CHECK_ROLE -->|manager| MANAGER_PERMS[✅ All Leads<br/>✅ All Scores<br/>✅ Reports<br/>✅ Dashboard<br/>❌ User Management]
    
    CHECK_ROLE -->|sales| SALES_PERMS[✅ Assigned Leads Only<br/>✅ Their Scores<br/>❌ Other Users' Data<br/>❌ Reports]
    
    CHECK_ROLE -->|viewer| VIEWER_PERMS[✅ Read-Only Access<br/>❌ No Scores Visible<br/>❌ No Editing<br/>❌ No Reports]
    
    ADMIN_PERMS --> ENDPOINT{Requested Endpoint}
    MANAGER_PERMS --> ENDPOINT
    SALES_PERMS --> ENDPOINT
    VIEWER_PERMS --> ENDPOINT
    
    ENDPOINT -->|GET /api/leads| CHECK_LEADS{Check Permission}
    ENDPOINT -->|POST /api/users| CHECK_USERS{Admin Only}
    ENDPOINT -->|GET /api/scores| CHECK_SCORES{Check Permission}
    
    CHECK_LEADS -->|admin/manager| ALLOW_ALL[Return All Leads]
    CHECK_LEADS -->|sales| FILTER[Return Assigned Leads<br/>WHERE assigned_to=user_id]
    CHECK_LEADS -->|viewer| ALLOW_READONLY[Return All Leads<br/>No Edit Allowed]
    
    CHECK_USERS -->|admin| ALLOW_MGMT[✅ Allow User CRUD]
    CHECK_USERS -->|Others| FORBID[❌ 403 Forbidden]
    
    CHECK_SCORES -->|admin/manager| ALLOW_SCORES[✅ Return Scores]
    CHECK_SCORES -->|sales| FILTER_SCORES[Return Scores<br/>for Assigned Leads Only]
    CHECK_SCORES -->|viewer| HIDE_SCORES[❌ 403 Forbidden]
    
    style ADMIN_PERMS fill:#4CAF50,stroke:#2E7D32,color:#fff
    style MANAGER_PERMS fill:#2196F3,stroke:#1565C0,color:#fff
    style SALES_PERMS fill:#FF9800,stroke:#E65100,color:#fff
    style VIEWER_PERMS fill:#9E9E9E,stroke:#616161,color:#fff
    style FORBID fill:#F44336,stroke:#C62828,color:#fff
```

---

## 10. Scaling Path (0 → 100K Companies)

```mermaid
graph TD
    subgraph "Current: 0-5K Companies"
        C1[Single Hetzner CX31<br/>4 vCPU, 8GB RAM<br/>€12.50/month]
        C1_DB[(Single PostgreSQL)]
        C1_WORKER[1 Celery Worker<br/>4 threads]
    end

    subgraph "Phase 2: 5-20K Companies"
        P2[Hetzner CX41<br/>8 vCPU, 16GB RAM<br/>€25/month]
        P2_DB[(PostgreSQL Primary)]
        P2_REPLICA[(Read Replica)]
        P2_WORKER[1 Celery Worker<br/>8 threads]
    end

    subgraph "Phase 3: 20-50K Companies"
        P3[Hetzner CX51<br/>16 vCPU, 32GB RAM<br/>€50/month]
        P3_DB[(PostgreSQL Primary<br/>Connection Pooling)]
        P3_REPLICA1[(Read Replica 1)]
        P3_REPLICA2[(Read Replica 2)]
        P3_WORKER1[Celery Worker 1<br/>8 threads]
        P3_WORKER2[Celery Worker 2<br/>8 threads]
        P3_LB[Load Balancer<br/>Nginx/HAProxy]
    end

    subgraph "Phase 4: 50-100K Companies"
        P4_K8S[Kubernetes Cluster<br/>€500+/month]
        P4_DB[(Managed PostgreSQL<br/>Hetzner/DigitalOcean)]
        P4_REDIS[(Redis Cluster<br/>3 nodes HA)]
        P4_BACKEND[3 Backend Pods<br/>Auto-scale 2-5]
        P4_WORKER[Worker Fleet<br/>Auto-scale 2-10]
        P4_CDN[CDN<br/>Cloudflare/BunnyCDN]
    end

    C1 -->|5K leads| P2
    P2 -->|20K leads| P3
    P3 -->|50K leads| P4_K8S

    C1_DB --> P2_DB
    P2_DB --> P3_DB
    P3_DB --> P4_DB

    style C1 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style P2 fill:#2196F3,stroke:#1565C0,color:#fff
    style P3 fill:#FF9800,stroke:#E65100,color:#fff
    style P4_K8S fill:#9C27B0,stroke:#6A1B9A,color:#fff
```

---

## How to Use These Diagrams

### View in VS Code
1. Install extension: "Markdown Preview Mermaid Support"
2. Open this file
3. Press `Ctrl+Shift+V` (Windows/Linux) or `Cmd+Shift+V` (Mac)
4. Diagrams render automatically

### Export as Images
1. Copy diagram code
2. Go to https://mermaid.live
3. Paste code in left panel
4. Click "Actions" → Download PNG/SVG/PDF

### Embed in Presentations
1. Export as SVG (vector, scales perfectly)
2. Import into PowerPoint/Google Slides/Keynote
3. Or use PNG for simpler workflows

### GitHub/GitLab
- Diagrams render automatically in markdown preview
- No installation needed
- Perfect for documentation

---

**Created:** July 13, 2026  
**Last Updated:** July 13, 2026  
**Version:** 1.0
