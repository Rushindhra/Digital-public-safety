"""Idempotently create the deployment bootstrap administrator and sample data."""
import logging
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.security import hash_password
from app.models.domain import FraudReport
from app.models.enums import ReportStatus, UserRole
from app.models.user import User

logger = logging.getLogger("dps-platform.seed")


async def seed() -> None:
    """Create bootstrap admin and demo fraud reports if collections are empty."""
    admin = await User.find_one(User.email == settings.ADMIN_EMAIL.lower())
    if not admin:
        admin = User(
            full_name=settings.ADMIN_FULL_NAME,
            email=settings.ADMIN_EMAIL.lower(),
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            preferred_language="en",
        )
        await admin.insert()
        logger.info("Created bootstrap administrator: %s", settings.ADMIN_EMAIL)
    else:
        logger.info("Bootstrap administrator already exists: %s", settings.ADMIN_EMAIL)

    report_count = await FraudReport.count()
    if report_count == 0:
        samples = [
            FraudReport(
                reporter_id=admin.id,
                category="digital_arrest",
                title="CBI impersonation call",
                description="Caller claimed to be CBI officer and demanded immediate transfer.",
                channel="call_transcript",
                risk_score=92.0,
                status=ReportStatus.INVESTIGATING,
                latitude=28.6139,
                longitude=77.2090,
                district="New Delhi",
                metadata={"source": "seed"},
            ),
            FraudReport(
                reporter_id=admin.id,
                category="counterfeit",
                title="Suspicious 500 INR note",
                description="Received fake currency at local market.",
                channel="web",
                risk_score=68.0,
                status=ReportStatus.TRIAGED,
                latitude=19.0760,
                longitude=72.8777,
                district="Mumbai",
                metadata={"source": "seed"},
            ),
            FraudReport(
                reporter_id=admin.id,
                category="phishing",
                title="UPI refund scam SMS",
                description="SMS asked to click link to receive refund.",
                channel="sms",
                risk_score=55.0,
                status=ReportStatus.SUBMITTED,
                latitude=12.9716,
                longitude=77.5946,
                district="Bengaluru",
                metadata={"source": "seed"},
            ),
        ]
        now = datetime.now(timezone.utc)
        for i, report in enumerate(samples):
            report.created_at = now - timedelta(days=len(samples) - i)
            await report.insert()
        logger.info("Seeded %d sample fraud reports", len(samples))



if __name__ == "__main__":
    import asyncio

    from app.db.mongodb import close_db, connect_db

    async def _run() -> None:
        await connect_db()
        await seed()
        await close_db()

    asyncio.run(_run())
