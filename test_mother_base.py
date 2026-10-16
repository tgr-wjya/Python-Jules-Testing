import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from database import SessionLocal, Base, engine
from models import Treasury


@pytest.fixture(autouse=True)
def setup_database():
    """Reset database state before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Seed initial treasury with 500,000 GMP if not present
    treasury = Treasury(id=1, gmp_balance=500000)
    db.add(treasury)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.mark.asyncio
async def test_health_check():
    """Verify health endpoint responds with operational status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OPERATIONAL"
        assert data["command"] == "Diamond Dogs Mother Base"


@pytest.mark.asyncio
async def test_get_treasury():
    """Verify treasury endpoint returns initial GMP balance."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/treasury")
        assert response.status_code == 200
        data = response.json()
        assert data["gmp_balance"] == 500000


@pytest.mark.asyncio
async def test_fulton_single_extraction():
    """Verify fultoned personnel are saved to Mother Base roster."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "codename": "Flaming Buffalo",
            "unit": "COMBAT",
            "rank": "A",
            "languages": "English, Kikongo"
        }
        response = await client.post("/fulton/extract", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["codename"] == "Flaming Buffalo"
        assert data["unit"] == "COMBAT"
        assert data["rank"] == "A"
        assert data["languages"] == "English, Kikongo"
        assert data["is_quarantined"] is False


@pytest.mark.asyncio
async def test_dispatch_single_deployment():
    """Verify single combat deployment deducts upfront GMP and creates mission."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "title": "Intercept the Arms Courier",
            "gmp_cost": 50000,
            "reward_gmp": 120000
        }
        response = await client.post("/dispatch/deploy", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Intercept the Arms Courier"
        assert data["gmp_cost"] == 50000
        assert data["status"] == "DEPLOYED"

        # Verify treasury was debited
        treasury_res = await client.get("/treasury")
        assert treasury_res.json()["gmp_balance"] == 450000


