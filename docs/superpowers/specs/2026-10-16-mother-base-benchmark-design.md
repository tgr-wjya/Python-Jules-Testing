# Mother Base Operations API (Diamond Dogs Benchmark)

## Overview
A lightweight Python REST API based on Metal Gear Solid V: The Phantom Pain (Diamond Dogs / Mother Base). The application manages Mother Base operations: Fulton personnel recovery, Combat unit dispatches, Treasury (GMP) accounting, and Medical Platform parasite quarantine.

The codebase is purposefully built with realistic, non-obvious engineering flaws categorized across Jules's three primary assessment pillars:
1. Performance (Event Loop Blocking)
2. Security & Data Integrity (TOCTOU Concurrency Race Condition)
3. Design & Architecture (In-Memory Filtering, N+1 Commits, Casing Inconsistency)

When scanned by Google Cloud's Jules, Jules should autonomously detect these categories, suggest patches, and generate pull requests that CodeRabbit can review.

## Technical Stack
- Language: Python 3.10+
- Web Framework: FastAPI (ASGI async framework)
- Database / ORM: SQLite via SQLAlchemy
- Data Validation: Pydantic v2
- Test Suite: Pytest with HTTPX (AsyncClient and TestClient)
- Process Manager: Uvicorn

## File Structure
```
.
├── database.py         # SQLite engine and session management
├── models.py           # SQLAlchemy database tables and Pydantic schemas
├── main.py             # FastAPI endpoints and operational logic
├── test_mother_base.py # Pytest test suite with baseline flows and trap reproductions
├── requirements.txt    # Project dependencies
└── README.md           # Diamond Dogs operational briefing and setup instructions
```

## Data Schema

### 1. Treasury (`treasury`)
Single-row state representing Mother Base's financial reserves.
- `id`: Integer, Primary Key (id=1)
- `gmp_balance`: Integer (Current Gross Military Product funds, initial seed: 500,000)

### 2. StaffMember (`staff_members`)
Personnel recovered via Fulton surface-to-air balloon.
- `id`: Integer, Primary Key, autoincrement
- `codename`: String(100), soldier codename (e.g., "Flaming Buffalo", "Laughing Wallaby")
- `unit`: String(50), assigned unit (`COMBAT`, `RD`, `MEDICAL`, `SUPPORT`, `INTEL`)
- `rank`: String(10), proficiency rank (`S_PLUS_PLUS`, `S`, `A`, `B`, `C`, `D`, `E`)
- `languages`: String(255), comma-separated languages spoken (e.g., "English, Kikongo")
- `is_quarantined`: Boolean, default False
- `created_at`: DateTime, timestamp of recruitment

### 3. DispatchMission (`dispatch_missions`)
Combat operations dispatched from Mother Base command.
- `id`: Integer, Primary Key, autoincrement
- `title`: String(150), mission title
- `gmp_cost`: Integer, upfront deployment fee
- `reward_gmp`: Integer, payout upon successful completion
- `status`: String(50), state (`PREPARING`, `DEPLOYED`, `COMPLETED`, `FAILED`)
- `created_at`: DateTime, dispatch creation timestamp

## Endpoints and Embedded Flaws

### 1. Staff Recovery (`POST /fulton/extract`)
- Purpose: Registers a recovered combatant onto Mother Base.
- Request Body:
  ```json
  {
    "codename": "Flaming Buffalo",
    "unit": "COMBAT",
    "rank": "A",
    "languages": "English, Kikongo"
  }
  ```
- Response: 201 Created with saved staff record.
- Jules Target Pillar: **Performance**
- Embedded Flaw (Event Loop Starvation):
  The handler is defined as `async def extract_soldier(...)`. To simulate Fulton balloon telemetry and aerial recovery delays, the implementation calls synchronous `time.sleep(1.5)` instead of an asynchronous sleep or non-blocking background queue. This halts the Python asyncio event loop, starving all concurrent requests on the single-worker process.
- Expected Resolution: Replace `time.sleep` with `asyncio.sleep` or handle background operations via non-blocking asynchronous tasks.

### 2. Combat Deployment (`POST /dispatch/deploy`)
- Purpose: Commits funds and deploys a strike team on a high-risk operation.
- Request Body:
  ```json
  {
    "title": "Intercept the Arms Courier",
    "gmp_cost": 50000,
    "reward_gmp": 120000
  }
  ```
- Response: 201 Created with mission status and updated GMP balance.
- Jules Target Pillar: **Security & Data Integrity**
- Embedded Flaw (TOCTOU Balance Race Condition):
  The endpoint verifies the treasury balance via:
  ```python
  treasury = db.query(Treasury).first()
  if treasury.gmp_balance < request.gmp_cost:
      raise HTTPException(status_code=400, detail="Insufficient GMP")
  await asyncio.sleep(0.05)  # brief processing delay
  treasury.gmp_balance -= request.gmp_cost
  db.commit()
  ```
  Because the read and the update are decoupled across an await point without atomic database updates or transaction row locks, concurrent dispatch requests can simultaneously pass the balance check and drive the Mother Base treasury into negative numbers.
- Expected Resolution: Execute an atomic conditional SQL update (e.g. `UPDATE treasury SET gmp_balance = gmp_balance - :cost WHERE gmp_balance >= :cost`) or enforce strict transaction locking.

### 3. Epidemic Isolation (`POST /quarantine/isolate-outbreak`)
- Purpose: Automatically moves all personnel speaking a target pathogen vector language into the Quarantine Platform to halt the Vocal Cord Parasite epidemic.
- Query Parameter: `target_language` (e.g. `kikongo`)
- Response: 200 OK with count of quarantined personnel.
- Jules Target Pillar: **Design & Performance**
- Embedded Flaw (In-Memory Scan, Loop Commits, Casing Inconsistency):
  The endpoint pulls the entire staff roster into Python memory:
  ```python
  all_staff = db.query(StaffMember).all()
  quarantined_count = 0
  for staff in all_staff:
      if target_language in staff.languages:
          staff.is_quarantined = True
          db.commit()
          quarantined_count += 1
  ```
  This creates three compounding issues:
  1. Memory and CPU overhead from loading all rows into Python memory rather than filtering in SQL.
  2. N+1 database transactions by calling `db.commit()` inside each iteration of the loop.
  3. Case sensitivity bug: `target_language in staff.languages` is case-sensitive, meaning searching for `"kikongo"` will miss staff recorded with `"Kikongo"`.
- Expected Resolution: Query the database directly with case-insensitive filtering (`ILIKE` or normalized lookup) and execute a single bulk update transaction.

### 4. Supporting Endpoints
- `GET /treasury`: Returns current Mother Base GMP balance and audit status.
- `GET /staff`: Returns list of staff members, with optional query filters for unit and quarantine status.
- `GET /health`: Fast health check endpoint to measure server responsiveness.

## Test Strategy and Verification Harness

A comprehensive test suite in `test_mother_base.py` will provide automated regression and verification checks:

1. `test_health_and_treasury`: Validates initial treasury balance (500,000 GMP) and health check baseline.
2. `test_fulton_recovery_flow`: Validates standard single-personnel extraction.
3. `test_dispatch_deployment_flow`: Validates standard dispatch deployment and balance deduction.
4. `test_fulton_event_loop_concurrency`:
   Fires a Fulton extraction and a health check concurrently. Asserts that the health check responds in under 200ms while the extraction proceeds. Demonstrates event loop starvation when `time.sleep` is present.
5. `test_concurrent_dispatches_prevent_negative_gmp`:
   Sets treasury balance to 50,000 GMP and sends two concurrent 50,000 GMP dispatches via `asyncio.gather`. Asserts that exactly one succeeds, one fails with 400 Insufficient GMP, and the final treasury balance is exactly 0. Demonstrates TOCTOU failure when concurrency control is missing.
6. `test_quarantine_case_insensitivity_and_bulk_isolation`:
   Seeds soldiers with mixed casing (`"English, Kikongo"`, `"kikongo, Afrikaans"`, `"Russian"`). Invokes isolation with `target_language="kikongo"`. Asserts that both Kikongo speakers are isolated and the non-speaker remains active. Demonstrates case-matching flaw.

## Verification Commands
- Install dependencies: `rtk pip install -r requirements.txt`
- Run test suite: `rtk pytest -v`
- Run server: `rtk uvicorn main:app --port 8000`
