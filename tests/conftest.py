import aiojobs
import pytest
from structlog.testing import capture_logs

from events.config import AppConfig
from events.transports.queue import AsyncInMemoryTransport


@pytest.fixture(scope="session")
def config():
    """Config for tests."""
    return AppConfig(defaults={"debug": False})


@pytest.fixture(scope="function")
def captured_logs():
    """Logs, captured during test execution."""
    with capture_logs() as logs:
        yield logs


@pytest.fixture
async def transport():
    """Transport for tests."""
    transport = AsyncInMemoryTransport()

    await transport.connect()

    yield transport

    await transport.close()


@pytest.fixture
async def scheduler():
    """Scheduler for background jobs."""
    scheduler = await aiojobs.create_scheduler()

    yield scheduler

    await scheduler.close()
