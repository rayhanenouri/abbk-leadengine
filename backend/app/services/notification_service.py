"""
Notification service - creates notifications for hot leads and score spikes.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Notification, NotificationType, User, UserRole, Lead


async def create_hot_lead_notification(
    db_session: AsyncSession,
    lead_id: int,
    new_score: float,
    old_score: float,
    service_name: str,
):
    """
    Create notification when lead becomes hot (score >= 70).

    Notifies all managers and admins.
    """
    # Get lead info
    result = await db_session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        return

    # Get all managers and admins
    result = await db_session.execute(
        select(User).where(
            User.is_active == True,
            User.role.in_([UserRole.admin, UserRole.manager])
        )
    )
    users = result.scalars().all()

    # Create notification for each user
    for user in users:
        notification = Notification(
            user_id=user.id,
            notification_type=NotificationType.hot_lead,
            title=f"🔥 Hot Lead: {lead.company_name}",
            message=f"{lead.company_name} is now a HIGH PRIORITY lead with {int(new_score)}/100 for {service_name}. Call them today!",
            lead_id=lead_id,
            extra_data={
                "old_score": old_score,
                "new_score": new_score,
                "service_name": service_name,
                "company_name": lead.company_name,
            }
        )
        db_session.add(notification)

    await db_session.commit()


async def create_score_spike_notification(
    db_session: AsyncSession,
    lead_id: int,
    new_score: float,
    old_score: float,
    service_name: str,
):
    """
    Create notification when score increases by 30+ points.

    Notifies all managers and admins.
    """
    score_increase = new_score - old_score

    # Get lead info
    result = await db_session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        return

    # Get all managers and admins
    result = await db_session.execute(
        select(User).where(
            User.is_active == True,
            User.role.in_([UserRole.admin, UserRole.manager])
        )
    )
    users = result.scalars().all()

    # Create notification for each user
    for user in users:
        notification = Notification(
            user_id=user.id,
            notification_type=NotificationType.score_spike,
            title=f"📈 Score Spike: {lead.company_name}",
            message=f"{lead.company_name} score jumped +{int(score_increase)} points (now {int(new_score)}/100) for {service_name}. Check what changed!",
            lead_id=lead_id,
            extra_data={
                "old_score": old_score,
                "new_score": new_score,
                "score_increase": score_increase,
                "service_name": service_name,
                "company_name": lead.company_name,
            }
        )
        db_session.add(notification)

    await db_session.commit()


async def create_new_signal_notification(
    db_session: AsyncSession,
    lead_id: int,
    signal_type: str,
    signal_title: str,
):
    """
    Create notification for high-value signals.

    Only for signals that indicate buying intent:
    - funding
    - audit_signal
    - multinational_signal
    - tender_detected
    """
    high_value_signals = ['funding', 'audit_signal', 'multinational_signal', 'tender_detected']

    if signal_type not in high_value_signals:
        return

    # Get lead info
    result = await db_session.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        return

    # Get all managers and admins
    result = await db_session.execute(
        select(User).where(
            User.is_active == True,
            User.role.in_([UserRole.admin, UserRole.manager])
        )
    )
    users = result.scalars().all()

    # Create notification for each user
    signal_emoji = {
        'funding': '💰',
        'audit_signal': '✅',
        'multinational_signal': '🏢',
        'tender_detected': '📋',
    }.get(signal_type, '🔔')

    for user in users:
        notification = Notification(
            user_id=user.id,
            notification_type=NotificationType.new_signal,
            title=f"{signal_emoji} New Signal: {lead.company_name}",
            message=f"{signal_title} detected for {lead.company_name}. This is a high-value signal!",
            lead_id=lead_id,
            extra_data={
                "signal_type": signal_type,
                "signal_title": signal_title,
                "company_name": lead.company_name,
            }
        )
        db_session.add(notification)

    await db_session.commit()
