import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from main import app
from core.models.base import Base
from core.utils.database import DatabaseHelper


# Test database URL
SQLALCHEMY_TEST_DATABASE_URL = "postgresql+asyncpg://postgres:12345@localhost:5432/institution_portal_test"

# Create async engine and session factory for testing
test_engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Override the async session_getter dependency
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# Apply the dependency override
app.dependency_overrides[DatabaseHelper.session_getter] = override_get_db

@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Create tables
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop tables


@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        # Use await and a lambda function to wrap the synchronous call
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn))
    yield
    async with test_engine.begin() as conn:
        # Use await and a lambda function for the drop operation as well
        await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn))

# Fixture for the test client
@pytest.fixture(scope="function")
def client(test_db):
    return TestClient(app)
