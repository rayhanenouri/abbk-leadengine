# ABBK Platform — Setup Guide

## Prerequisites (Ubuntu 24.04)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose plugin
sudo apt install docker-compose-plugin

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
docker --version
docker compose version
```

## First-time setup

```bash
# 1. Clone or create project
cd ~/projects
git clone <your-repo> abbk-platform
cd abbk-platform

# 2. Configure environment
cp .env.example .env
nano .env   # fill in: POSTGRES_PASSWORD, SECRET_KEY, ANTHROPIC_API_KEY, APIFY_API_TOKEN

# Generate a strong SECRET_KEY:
openssl rand -hex 32

# 3. Run setup script
chmod +x scripts/start.sh
./scripts/start.sh
```

## Daily development commands

```bash
# Start everything
docker compose up -d

# Watch all logs
docker compose logs -f

# Watch only one service
docker compose logs -f backend

# Restart one service after code changes (hot-reload handles most cases)
docker compose restart backend

# Run a database migration
docker compose run --rm backend alembic revision --autogenerate -m "add table"
docker compose run --rm backend alembic upgrade head

# Open a Python shell inside the backend container
docker compose exec backend python

# Open a psql shell
docker compose exec db psql -U abbk_user -d abbk_platform

# Stop everything (keeps data)
docker compose down

# Stop and wipe all data (fresh start)
docker compose down -v
```

## Ports

| Service   | URL                         |
|-----------|-----------------------------|
| Frontend  | http://localhost:5173        |
| API       | http://localhost:8000        |
| API docs  | http://localhost:8000/docs   |
| Flower    | http://localhost:5555        |
| DB        | localhost:5432               |
| Redis     | localhost:6379               |

## Folder structure

```
abbk-platform/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entrypoint
│   │   ├── core/config.py       ← all settings from .env
│   │   ├── db/session.py        ← SQLAlchemy async engine
│   │   ├── models/models.py     ← all database tables
│   │   ├── schemas/             ← Pydantic request/response models
│   │   ├── api/routes/          ← one file per route group
│   │   │   ├── auth.py
│   │   │   ├── leads.py
│   │   │   ├── users.py
│   │   │   ├── scores.py
│   │   │   └── scraping.py
│   │   ├── services/
│   │   │   └── scoring_engine.py ← rule-based scoring + AI signal extraction
│   │   └── workers/
│   │       ├── celery_app.py    ← Celery config + beat schedule
│   │       └── tasks/           ← scraping.py, scoring.py, enrichment.py
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/                     ← React components
│   ├── Dockerfile
│   └── package.json
├── scraper/
│   ├── spiders/                 ← Scrapy spiders (directories, news, jobs)
│   └── utils/                   ← shared scraping helpers
├── docker/
│   ├── nginx.conf
│   └── init.sql                 ← enables pgvector on first DB start
├── scripts/
│   └── start.sh
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Next steps after setup

1. Initialize the React frontend: `cd frontend && npm create vite@latest . -- --template react && npm install`
2. Initialize Alembic: `docker compose run --rm backend alembic init alembic`
3. Create your first migration: `docker compose run --rm backend alembic revision --autogenerate -m "initial"`
4. Run it: `docker compose run --rm backend alembic upgrade head`
5. Start building routes in `backend/app/api/routes/`
