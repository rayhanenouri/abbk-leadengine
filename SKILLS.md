# SKILLS.md — How Claude Code Works on This Project

## Code Style
- Python: PEP8, type hints everywhere
- FastAPI: always async def for route handlers
- SQLAlchemy: always async session from get_db dependency
- Pydantic: always validate input and output with schemas
- Error handling: always HTTPException with correct status codes
- Logging: use loguru logger never print in production

## FastAPI Route Pattern
@router.get("/leads", response_model=List[LeadResponse])
async def get_leads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

## Admin Route Pattern
@router.get("/users")
async def get_users(
    current_user: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db)
):

## Duplicate Check Before Every Lead Insert
existing = await db.execute(
    select(Lead).where(
        or_(Lead.website == website, Lead.company_name == name)
    )
)
if existing.scalar_one_or_none():
    return  # skip duplicate — never create duplicates

## Async DB Query Pattern
result = await db.execute(select(Lead).where(Lead.id == lead_id))
lead = result.scalar_one_or_none()

## Store Raw Scraped Data Pattern
lead.scraped_data["source_name"] = {
    "raw_text": extracted_text,
    "scraped_at": datetime.utcnow().isoformat()
}

## Create Signal After Every Detection
signal = LeadSignal(
    lead_id=lead.id,
    signal_type="new_hire",
    title="Company hiring mechanical engineer",
    detail=job_title,
    source_url=job_url,
    detected_at=datetime.utcnow()
)
db.add(signal)

## Celery Task Registration Pattern
"task-name": {
    "task": "app.workers.tasks.scraping.function_name",
    "schedule": crontab(hour="*/6"),
}

## Claude API Caching Pattern — Never Re-call Same Text
cached = lead.scraped_data.get("claude_signals")
if cached:
    return cached
result = await call_claude_api(text)
lead.scraped_data["claude_signals"] = result
await db.commit()
return result

## Alembic Migration — Always Run After Model Change
docker compose run --rm backend alembic revision --autogenerate -m "description"
docker compose run --rm backend alembic upgrade head

## Git Commit Pattern
feat: short description of new feature
fix: short description of bug fixed
chore: configuration or setup change

## Verification After Every Issue
After route: curl http://localhost:8000/api/endpoint
After DB change: docker compose exec db psql -U abbk_user -d abbk_LeadEngine -c "SELECT COUNT(*) FROM leads;"
After scraper: docker compose exec db psql -U abbk_user -d abbk_LeadEngine -c "SELECT company_name, city FROM leads LIMIT 10;"
