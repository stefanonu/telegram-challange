import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport

from app.main import app
from app.db import Base
from app.db import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_process_request_once():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/process-request", json={
            "request_id": "abc123",
            "payload": {"some": "data"}
        })
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

@pytest.mark.asyncio
async def test_process_request_duplicate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/process-request", json={
            "request_id": "abc123",
            "payload": {"some": "data"}
        })
        assert response.status_code == 200
        assert response.json()["status"] == "duplicate"
