"""Shared test fixtures — async database sessions, test client, mock data."""

import uuid
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.core.config import Settings
from app.main import app


TEST_DATABASE_URL = "postgresql+asyncpg://ludo:ludo_secret@localhost:5432/ludo_legends_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture
async def test_user(db: AsyncSession):
    from app.models.user import User, UserRole
    user = User(
        id=str(uuid.uuid4()),
        phone=f"+91{uuid.uuid4().hex[:10]}",
        name="Test Player",
        role=UserRole.PLAYER,
        is_active=True,
        is_verified=True,
        referral_code=f"LL{uuid.uuid4().hex[:8].upper()}",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db: AsyncSession):
    from app.models.user import User, UserRole
    admin = User(
        id=str(uuid.uuid4()),
        phone=f"+91{uuid.uuid4().hex[:10]}",
        name="Test Admin",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        referral_code=f"LL{uuid.uuid4().hex[:8].upper()}",
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def super_admin(db: AsyncSession):
    from app.models.user import User, UserRole
    admin = User(
        id=str(uuid.uuid4()),
        phone=f"+91{uuid.uuid4().hex[:10]}",
        name="Super Admin",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        is_verified=True,
        referral_code=f"LL{uuid.uuid4().hex[:8].upper()}",
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def user_token(test_user) -> str:
    from app.core.security import create_access_token
    return create_access_token({"sub": test_user.id, "role": test_user.role.value})


@pytest_asyncio.fixture
async def admin_token(test_admin) -> str:
    from app.core.security import create_access_token
    return create_access_token({"sub": test_admin.id, "role": test_admin.role.value})


@pytest_asyncio.fixture
async def super_admin_token(super_admin) -> str:
    from app.core.security import create_access_token
    return create_access_token({"sub": super_admin.id, "role": super_admin.role.value})


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
