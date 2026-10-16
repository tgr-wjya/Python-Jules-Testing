# Mother Base Operations API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a focused MGSV-themed FastAPI application with realistic embedded flaws across Security, Performance, and Design pillars to benchmark Google Cloud's Jules and CodeRabbit.

**Architecture:** A compact FastAPI service backed by SQLite/SQLAlchemy providing Fulton personnel recovery, Combat dispatches with treasury accounting, and Kikongo vocal cord parasite quarantine isolation, verified by a comprehensive Pytest test suite.

**Tech Stack:** Python 3.10+, FastAPI, SQLAlchemy, Pydantic v2, SQLite, Pytest, HTTPX, Uvicorn.

**Spec:** docs/superpowers/specs/2026-10-16-mother-base-benchmark-design.md

## Global Constraints

- Python 3.10+ compatibility.
- Zero-emoji rule across all source code, comments, test logs, terminal messages, and documentation.
- All dependencies must be listed in `requirements.txt` with standard version pins.
- Database runs locally on SQLite (`mother_base.db`).
- Code must look clean, realistic, and idiomatic on the surface, without artificial syntax errors or obvious linter violations.

## Review Focus

- Concurrency under SQLite: Ensure SQLite supports the test client concurrent connections (e.g. check_same_thread=False).
- Pydantic v2 compatibility: Use `model_config = ConfigDict(from_attributes=True)` instead of legacy v1 `orm_mode = True`.
- Pytest async markers: Ensure `pytest-asyncio` or `anyio` is configured properly so async tests execute reliably.
- Database cleanup between test cases: Ensure tests do not leak mutated state into subsequent tests.
- Casing consistency in quarantine lookups: Ensure tests explicitly verify case differences (`Kikongo` vs `kikongo`).

---

### Task 1: Project Scaffolding & Data Layer

**Files:**
- Create: `requirements.txt`
- Create: `database.py`
- Create: `models.py`
- Test: `test_mother_base.py`

**Interfaces:**
- Produces:
  - `database.py`: `Base`, `engine`, `SessionLocal`, `get_db() -> Generator[Session, None, None]`
  - `models.py`:
    - SQLAlchemy: `Treasury`, `StaffMember`, `DispatchMission`
    - Pydantic: `StaffCreate`, `StaffResponse`, `DispatchCreate`, `DispatchResponse`, `TreasuryResponse`, `QuarantineResponse`

- [ ] **Step 1: Define `requirements.txt`**
Add:
```
fastapi>=0.110.0
uvicorn>=0.28.0
sqlalchemy>=2.0.0
pydantic>=2.6.0
httpx>=0.27.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

- [ ] **Step 2: Create `database.py`**
Setup SQLite engine with `check_same_thread=False`, `sessionmaker`, declarative base, and a `get_db` FastAPI dependency generator.

- [ ] **Step 3: Create `models.py`**
Implement SQLAlchemy tables (`Treasury`, `StaffMember`, `DispatchMission`) and corresponding Pydantic v2 schemas for requests and responses.

- [ ] **Step 4: Install dependencies in local virtualenv**
Run: `rtk pip install -r requirements.txt`
Expected: Successfully installed packages.

- [ ] **Step 5: Write initial model test and verify table creation**
Verify tables create cleanly via `Base.metadata.create_all(bind=engine)`.
Run: `rtk python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine); print('OK')"`
Expected: Prints `OK`.

- [ ] **Step 6: Commit**
```bash
git add requirements.txt database.py models.py
git commit -m "feat: add database configuration and data models"
```

---

### Task 2: Core Application & Health/Treasury Endpoints

**Files:**
- Create: `main.py`
- Modify: `test_mother_base.py`

**Interfaces:**
- Consumes: `database.py` (`get_db`, `engine`, `Base`), `models.py` (`Treasury`, `TreasuryResponse`)
- Produces:
  - `main.py`: `app = FastAPI(...)`
  - Routes: `GET /health`, `GET /treasury`, `GET /staff`

- [ ] **Step 1: Write test for health and initial treasury state**
In `test_mother_base.py`, write `test_health_check` and `test_get_treasury`.
Expected initial treasury balance: 500,000 GMP.

- [ ] **Step 2: Run test to verify it fails**
Run: `rtk pytest test_mother_base.py -k "test_health_check"`
Expected: FAIL (file or module main not found).

- [ ] **Step 3: Implement `main.py` core routes and startup seed**
Initialize FastAPI app, create tables on startup, ensure initial `Treasury` record exists with 500,000 GMP, implement `GET /health`, `GET /treasury`, and `GET /staff`.

- [ ] **Step 4: Run test to verify it passes**
Run: `rtk pytest test_mother_base.py -k "test_health_check or test_get_treasury" -v`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add main.py test_mother_base.py
git commit -m "feat: add core FastAPI app and treasury endpoints"
```

---

### Task 3: Fulton Recovery Endpoint with Event Loop Starvation Flaw

**Files:**
- Modify: `main.py`
- Modify: `test_mother_base.py`

**Interfaces:**
- Consumes: `models.py` (`StaffMember`, `StaffCreate`, `StaffResponse`)
- Produces: `POST /fulton/extract`

- [ ] **Step 1: Write standard extraction test and concurrency starvation test**
In `test_mother_base.py`:
- `test_fulton_single_extraction`: Verifies soldier is persisted with correct codename and attributes.
- `test_fulton_event_loop_starvation`: Verifies whether synchronous blocking occurs during Fulton extraction by measuring concurrent health check latency.

- [ ] **Step 2: Implement `POST /fulton/extract` in `main.py`**
Implement `async def extract_soldier(payload: StaffCreate, db: Session = Depends(get_db)):`
Include `import time; time.sleep(1.0)` to simulate Fulton telemetry uplink.

- [ ] **Step 3: Run tests**
Run: `rtk pytest test_mother_base.py -k "test_fulton_single_extraction" -v`
Expected: PASS for single extraction.

- [ ] **Step 4: Commit**
```bash
git add main.py test_mother_base.py
git commit -m "feat: add fulton extraction endpoint with telemetry delay"
```

---

### Task 4: Combat Deployment Endpoint with TOCTOU Concurrency Flaw

**Files:**
- Modify: `main.py`
- Modify: `test_mother_base.py`

**Interfaces:**
- Consumes: `models.py` (`DispatchMission`, `DispatchCreate`, `DispatchResponse`, `Treasury`)
- Produces: `POST /dispatch/deploy`

- [ ] **Step 1: Write single dispatch test and concurrent dispatch race condition test**
In `test_mother_base.py`:
- `test_dispatch_single_deployment`: Deploys mission costing 50,000 GMP, checks balance drops to 450,000.
- `test_concurrent_dispatches_balance_integrity`: Sets treasury to 50,000 GMP. Launches 2 concurrent dispatches costing 50,000 each. Asserts balance does not become negative.

- [ ] **Step 2: Implement `POST /dispatch/deploy` in `main.py`**
Implement `async def deploy_mission(...)` with decoupled check and deduction:
```python
treasury = db.query(Treasury).first()
if treasury.gmp_balance < payload.gmp_cost:
    raise HTTPException(status_code=400, detail="Insufficient GMP")
await asyncio.sleep(0.05)
treasury.gmp_balance -= payload.gmp_cost
db.commit()
```

- [ ] **Step 3: Run single dispatch test**
Run: `rtk pytest test_mother_base.py -k "test_dispatch_single_deployment" -v`
Expected: PASS.

- [ ] **Step 4: Commit**
```bash
git add main.py test_mother_base.py
git commit -m "feat: add combat dispatch deployment endpoint"
```

---

### Task 5: Parasite Quarantine Platform with In-Memory / Case-Sensitivity Flaw

**Files:**
- Modify: `main.py`
- Modify: `test_mother_base.py`

**Interfaces:**
- Consumes: `models.py` (`StaffMember`, `QuarantineResponse`)
- Produces: `POST /quarantine/isolate-outbreak`

- [ ] **Step 1: Write quarantine isolation test**
In `test_mother_base.py`:
- Seed 3 soldiers: one with `"English, Kikongo"`, one with `"kikongo, Afrikaans"`, one with `"Russian"`.
- Call `/quarantine/isolate-outbreak?target_language=kikongo`.
- Assert both Kikongo speakers are isolated and non-speaker is untouched.

- [ ] **Step 2: Implement `POST /quarantine/isolate-outbreak` in `main.py`**
Implement endpoint with full-table memory load, case-sensitive `in` check, and commit in loop:
```python
all_staff = db.query(StaffMember).all()
quarantined_count = 0
for staff in all_staff:
    if target_language in staff.languages:
        staff.is_quarantined = True
        db.commit()
        quarantined_count += 1
```

- [ ] **Step 3: Run single-case quarantine test**
Verify endpoint executes and returns correct response format.

- [ ] **Step 4: Commit**
```bash
git add main.py test_mother_base.py
git commit -m "feat: add parasite quarantine isolation endpoint"
```

---

### Task 6: Test Suite & Reproduction Harness Finalization

**Files:**
- Modify: `test_mother_base.py`

**Interfaces:**
- Validates all baseline operational routes and documents the three challenge test cases.

- [ ] **Step 1: Organize test suite into baseline tests and benchmark challenge tests**
Ensure `test_mother_base.py` contains:
- `test_baseline_operational_flow` (Full operational cycle: extraction, dispatch, quarantine, verification)
- `test_challenge_performance_event_loop`
- `test_challenge_security_concurrency_race`
- `test_challenge_design_quarantine_casing`

- [ ] **Step 2: Run test suite**
Run: `rtk pytest test_mother_base.py -v`
Expected: Baseline tests PASS; challenge tests clearly reproduce the three targeted flaws.

- [ ] **Step 3: Commit**
```bash
git add test_mother_base.py
git commit -m "test: complete mother base benchmark test suite"
```

---

### Task 7: Operational Documentation & Briefing

**Files:**
- Create: `README.md`

- [ ] **Step 1: Author `README.md`**
Write Diamond Dogs operational manual:
- Mother Base background and system architecture.
- Local setup and testing commands (`pip install`, `pytest`, `uvicorn`).
- Architecture breakdown across Performance, Security, and Design.

- [ ] **Step 2: Commit**
```bash
git add README.md
git commit -m "docs: add Mother Base operational readme"
```
