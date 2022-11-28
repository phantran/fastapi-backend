import os

os.environ["ENV"] = "test"  # noqa

import asyncio

from _pytest.fixtures import fixture
from httpx import AsyncClient

from app.server import app
from core.db import Base
from core.db.session import engine
from core.fastapi.middlewares import AuthBackend
from core.fastapi.schemas import CurrentUser


@fixture
def client(access_token, monkeypatch) -> AsyncClient:
    """
    Patch the auth handler to skip regular auth checks
    and provide a test tenant by default.
    """

    async def authenticate(self, x):
        return "access_token", CurrentUser(id=1)

    monkeypatch.setattr(AuthBackend, "authenticate", authenticate)
    c = AsyncClient(app=app, base_url="http://test")
    c.headers.update({"Authorization": f"Bearer {access_token}"})
    return c


@fixture
def access_token() -> str:
    return "access_token"


@fixture
def test_db():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_models())
