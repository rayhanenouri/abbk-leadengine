# How to Access ABBK LeadEngine Database

## Method 1: Via Docker (Easiest)

```bash
# Access PostgreSQL shell
docker compose exec db psql -U abbk_user -d abbk_LeadEngine

# Once inside, run SQL queries:
SELECT COUNT(*) FROM leads;
SELECT * FROM leads LIMIT 10;
SELECT company_name, website, country FROM leads;
\q  # to quit
```

## Method 2: One-Line Commands

```bash
# Count total leads
docker compose exec db psql -U abbk_user -d abbk_LeadEngine -c "SELECT COUNT(*) FROM leads;"

# View all leads with details
docker compose exec db psql -U abbk_user -d abbk_LeadEngine -c "SELECT id, company_name, website, country, city FROM leads ORDER BY id DESC LIMIT 20;"

# View leads with websites only
docker compose exec db psql -U abbk_user -d abbk_LeadEngine -c "SELECT company_name, website FROM leads WHERE website IS NOT NULL AND website != '';"

# View lead signals
docker compose exec db psql -U abbk_user -d abbk_LeadEngine -c "SELECT * FROM lead_signals LIMIT 10;"

# View scores
docker compose exec db psql -U abbk_user -d abbk_LeadEngine -c "SELECT * FROM lead_scores LIMIT 10;"
```

## Method 3: Using pgAdmin or DBeaver (GUI)

**Connection Details:**
- Host: `localhost` (if running locally) or your VPS IP
- Port: `5432` (exposed in docker-compose)
- Database: `abbk_LeadEngine`
- Username: `abbk_user`
- Password: (check your .env file)

## Method 4: Export to CSV

```bash
# Export all leads to CSV
docker compose exec db psql -U abbk_user -d abbk_LeadEngine -c "\COPY (SELECT company_name, website, country, city, sector FROM leads) TO STDOUT WITH CSV HEADER" > leads_export.csv

# View the CSV
cat leads_export.csv
```

## Common Queries

```sql
-- Total leads by country
SELECT country, COUNT(*) as count FROM leads GROUP BY country ORDER BY count DESC;

-- Leads with websites
SELECT COUNT(*) FROM leads WHERE website IS NOT NULL AND website != '';

-- Recent leads (last 24 hours)
SELECT company_name, created_at FROM leads WHERE created_at > NOW() - INTERVAL '24 hours';

-- Delete all leads (CAREFUL!)
DELETE FROM lead_signals;
DELETE FROM lead_scores;  
DELETE FROM leads;
```

## Database Schema

**Tables:**
- `leads` - All companies
- `lead_signals` - Hiring signals, news mentions, etc.
- `lead_scores` - Scores per ABBK product
- `users` - System users
- `services` - ABBK products/services

**View schema:**
```bash
docker compose exec db psql -U abbk_user -d abbk_LeadEngine -c "\d leads"
```
