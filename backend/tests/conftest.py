"""Pytest configuration and MongoDB mock fixtures."""
import os

import pytest
import pytest_asyncio
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient

from app.models.domain import Evidence, FraudReport, Notification
from app.models.user import User

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB_NAME", "digital_public_safety_test")
os.environ["DEBUG"] = "false"

DOCUMENT_MODELS = [User, FraudReport, Evidence, Notification]
_mock_client = AsyncMongoMockClient()
DB_NAME = "digital_public_safety_test"


async def _init_mock_db() -> None:
    database = _mock_client[DB_NAME]
    await init_beanie(database=database, document_models=DOCUMENT_MODELS)


async def _mock_connect_db() -> None:
    await _init_mock_db()
    from app.db.seed import seed

    await seed()


async def _mock_close_db() -> None:
    return None


@pytest_asyncio.fixture(autouse=True)
async def setup_test_database(monkeypatch):
    """Route all database access through an in-memory MongoDB mock."""
    monkeypatch.setattr("app.db.mongodb.connect_db", _mock_connect_db)
    monkeypatch.setattr("app.db.mongodb.close_db", _mock_close_db)
    await _mock_connect_db()
    yield
    await _mock_client.drop_database(DB_NAME)
