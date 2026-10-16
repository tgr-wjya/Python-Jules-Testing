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


@pytest.mark.asyncio
async def test_quarantine_single_case_matching():
    """Verify quarantine isolation sets is_quarantined for matching staff."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Seed staff with exact match "Kikongo"
        payload = {
            "codename": "Laughing Wallaby",
            "unit": "MEDICAL",
            "rank": "B",
            "languages": "English, Kikongo"
        }
        await client.post("/fulton/extract", json=payload)

        # Trigger isolation with exact casing
        res = await client.post("/quarantine/isolate-outbreak", params={"target_language": "Kikongo"})
        assert res.status_code == 200
        assert res.json()["isolated_count"] == 1
        assert res.json()["target_language"] == "Kikongo"

        # Verify staff record is now quarantined
        staff_res = await client.get("/staff", params={"quarantined": True})
        assert len(staff_res.json()) == 1
        assert staff_res.json()[0]["codename"] == "Laughing Wallaby"


@pytest.mark.asyncio
async def test_baseline_operational_flow():
    """
    Verify complete operational cycle for Mother Base:
    Health check -> Staff Fulton -> Treasury Check -> Dispatch Deployment -> Quarantine Filter.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        h = await client.get("/health")
        assert h.status_code == 200

        # 2. Extract soldiers
        s1 = await client.post("/fulton/extract", json={
            "codename": "Amber Fox",
            "unit": "COMBAT",
            "rank": "S",
            "languages": "English"
        })
        assert s1.status_code == 201

        s2 = await client.post("/fulton/extract", json={
            "codename": "Grizzly Bear",
            "unit": "RD",
            "rank": "A",
            "languages": "French"
        })
        assert s2.status_code == 201

        # 3. Check treasury
        t = await client.get("/treasury")
        assert t.json()["gmp_balance"] == 500000

        # 4. Deploy mission
        d = await client.post("/dispatch/deploy", json={
            "title": "Sabotage the Fuel Reserves",
            "gmp_cost": 75000,
            "reward_gmp": 180000
        })
        assert d.status_code == 201
        assert d.json()["status"] == "DEPLOYED"

        # 5. Verify treasury deduction
        t_after = await client.get("/treasury")
        assert t_after.json()["gmp_balance"] == 425000

        # 6. List staff
        all_s = await client.get("/staff")
        assert len(all_s.json()) == 2


# Jules Benchmark Challenge Tests



@pytest.mark.asyncio
async def test_challenge_performance_event_loop():
    """
    [PERFORMANCE PILLAR CHALLENGE]
    Fulton extraction should not block the ASGI event loop.
    A lightweight health check dispatched alongside extraction should respond in under 200ms.
    Fails when time.sleep() blocks the event loop thread.
    """
    import asyncio
    import time

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "codename": "Silent Mastiff",
            "unit": "INTEL",
            "rank": "B",
            "languages": "English"
        }

        start = time.perf_counter()
        fulton_task = asyncio.create_task(client.post("/fulton/extract", json=payload))
        # Yield to let fulton_task enter handler.
        # If handler blocks with time.sleep(), thread is frozen and sleep(0.005) cannot resume until sleep finishes.
        await asyncio.sleep(0.005)

        health_res = await client.get("/health")
        total_health_time = time.perf_counter() - start

        fulton_res = await fulton_task

        assert fulton_res.status_code == 201
        assert health_res.status_code == 200
        assert total_health_time < 0.2, (
            f"Event loop blocked! Health check took {total_health_time:.3f}s. "
            "Ensure async handlers do not use synchronous blocking delays."
        )


@pytest.mark.asyncio
async def test_challenge_security_concurrency_race():
    """
    [SECURITY & DATA INTEGRITY PILLAR CHALLENGE]
    Concurrent dispatch mission deployments must preserve treasury solvency.
    When treasury has exactly 50,000 GMP, two simultaneous 50,000 GMP dispatches
    must result in exactly ONE approval (201) and ONE rejection (400), with final GMP >= 0.
    Fails when TOCTOU race allows negative GMP balances.
    """
    import asyncio

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Drain treasury to exactly 50,000 GMP
        db = SessionLocal()
        treasury = db.query(Treasury).filter(Treasury.id == 1).first()
        treasury.gmp_balance = 50000
        db.commit()
        db.close()

        payload = {
            "title": "Emergency FOB Defense",
            "gmp_cost": 50000,
            "reward_gmp": 100000
        }

        # Dispatch two operations simultaneously
        res1, res2 = await asyncio.gather(
            client.post("/dispatch/deploy", json=payload),
            client.post("/dispatch/deploy", json=payload),
        )

        statuses = sorted([res1.status_code, res2.status_code])

        treasury_res = await client.get("/treasury")
        final_gmp = treasury_res.json()["gmp_balance"]

        # Final treasury must never drop below 0
        assert final_gmp >= 0, (
            f"Treasury balance dropped below zero to {final_gmp} GMP! "
            "Race condition detected in concurrent fund verification."
        )
        assert statuses == [201, 400], (
            f"Expected one success (201) and one failure (400), got {statuses}. "
            "Concurrent balance check permitted overspending."
        )


@pytest.mark.asyncio
async def test_challenge_design_quarantine_casing():
    """
    [DESIGN & ARCHITECTURE PILLAR CHALLENGE]
    Quarantine protocol must detect pathogen vector languages case-insensitively.
    Staff speaking 'Kikongo', 'kikongo', or 'KIKONGO' must all be safely isolated.
    Fails when naive case-sensitive matching misses infected soldiers.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Seed 3 soldiers: two speak Kikongo (different casing), one does not
        soldiers = [
            {"codename": "Spiteful Badger", "unit": "COMBAT", "rank": "A", "languages": "English, Kikongo"},
            {"codename": "Cruel Crocodile", "unit": "RD", "rank": "B", "languages": "kikongo, Afrikaans"},
            {"codename": "Copper Greyhound", "unit": "SUPPORT", "rank": "B", "languages": "Russian, Pashto"},
        ]
        for s in soldiers:
            await client.post("/fulton/extract", json=s)

        # Trigger isolation with lowercase 'kikongo'
        res = await client.post("/quarantine/isolate-outbreak", params={"target_language": "kikongo"})
        assert res.status_code == 200
        data = res.json()

        # Both Kikongo speakers must be quarantined
        assert data["isolated_count"] == 2, (
            f"Expected 2 soldiers isolated, but only {data['isolated_count']} were quarantined. "
            "Case-sensitivity bug detected in language matching."
        )

        quarantined = await client.get("/staff", params={"quarantined": True})
        codenames = [s["codename"] for s in quarantined.json()]
        assert "Spiteful Badger" in codenames
        assert "Cruel Crocodile" in codenames
        assert "Copper Greyhound" not in codenames




