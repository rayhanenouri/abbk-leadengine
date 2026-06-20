from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import engine, Base
from app.api.routes import leads, users, scores, auth, scraping


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables if they don't exist
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Warning: Could not connect to database on startup: {e}")
        print("The application will start anyway, but database operations will fail.")
    yield
    # Shutdown: close DB connections
    try:
        await engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title="ABBK Platform API",
    version="0.1.0",
    description="B2B Lead Generation & Sales Intelligence for ABBK Physicsworks",
    lifespan=lifespan,
)

# CORS — allow the React frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80", "http://192.168.100.15:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route groups
app.include_router(auth.router,     prefix="/api/auth",     tags=["auth"])
app.include_router(users.router,    prefix="/api/users",    tags=["users"])
app.include_router(leads.router,    prefix="/api/leads",    tags=["leads"])
app.include_router(scores.router,   prefix="/api/scores",   tags=["scores"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["scraping"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
