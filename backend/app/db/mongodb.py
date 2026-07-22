"""
MongoDB connection and Beanie ODM initialization.
"""
import logging
from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.models.domain import Evidence, FraudReport, Notification
from app.models.user import User

logger = logging.getLogger("dps-platform.db")

_client: Optional[AsyncIOMotorClient] = None

DOCUMENT_MODELS = [User, FraudReport, Evidence, Notification]


async def connect_db() -> None:
    """Initialize Motor client and register Beanie document models.

    Ping MongoDB before Beanie initialisation so a missing or not-yet-ready
    database produces a concise, actionable startup error instead of a long
    server-selection traceback.
    """
    global _client
    client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
        connectTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
    )
    try:
        await client.admin.command("ping")
        database = client[settings.MONGODB_DB_NAME]
        await init_beanie(database=database, document_models=DOCUMENT_MODELS)
    except PyMongoError as exc:
        client.close()
        logger.error(
            "MongoDB is unavailable at %s. Start the MongoDB service or set "
            "MONGODB_URI to a reachable database.",
            settings.MONGODB_URI,
        )
        raise RuntimeError("MongoDB is unavailable; backend startup aborted.") from exc

    _client = client
    logger.info("Connected to MongoDB database: %s", settings.MONGODB_DB_NAME)


async def close_db() -> None:
    """Close the Motor client on application shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed")
