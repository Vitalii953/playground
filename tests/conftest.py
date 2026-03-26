import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

"""Shared fixtures available to all test subpackages.

This module is intentionally lean; more specific helpers live in the
subdirectories' own ``conftest.py`` files so that each test folder can
grow independently without dragging unrelated fixtures along.
"""


@pytest.fixture
def player():
    """Simple stub mimicking a ``Player`` instance.

    Only ``id`` and ``preferences`` attributes are used by the service
    tests, so the fixture provides those and nothing else.
    """

    p = MagicMock()
    p.id = uuid.uuid4()
    p.preferences = {}
    return p


@pytest.fixture
def mock_redis():
    """AsyncMock with the minimal Redis methods we call.

    Defaults to a cache miss; individual tests can modify
    ``mock_redis.get.return_value`` to simulate hits.
    """

    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    return redis


@pytest.fixture
def mock_postgres_db():
    """AsyncMock simulating a PostgreSQL session.

    It exposes ``add`` and ``commit`` so that service tests can verify
    that they were called without touching a real database.
    """

    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db
