"""
Celery tasks for database maintenance.
"""
from celery import shared_task
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from datetime import datetime, timedelta
import asyncio
import logging

from app.core.config import settings
from app.models.models import LeadSignal
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.maintenance.cleanup_old_signals")
def cleanup_old_signals_task():
    """
    Celery task wrapper for cleaning up old signals.

    Removes signals older than 1 year to keep DB clean.
    """
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(cleanup_old_signals())
    return result


async def cleanup_old_signals():
    """
    Remove signals older than 1 year.

    Keeps database size manageable and removes stale signals.
    """
    logger.info("Starting signal cleanup...")

    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        try:
            # Delete signals older than 1 year
            cutoff_date = datetime.utcnow() - timedelta(days=365)

            result = await session.execute(
                delete(LeadSignal).where(LeadSignal.detected_at < cutoff_date)
            )

            deleted_count = result.rowcount
            await session.commit()

            logger.info(f"Cleanup complete: {deleted_count} old signals removed")

            return {
                'deleted_count': deleted_count,
                'cutoff_date': cutoff_date.isoformat(),
            }

        except Exception as e:
            await session.rollback()
            logger.error(f"Error during cleanup: {e}")
            raise

        finally:
            await engine.dispose()
