# Diamond Dogs — Mother Base OS (Operations API)

Operational command and management REST API for Mother Base forces, designed as an autonomous AI agent benchmark for Google Cloud's Jules paired with CodeRabbit code reviews.

## Background & Intel

Mother Base coordinates Diamond Dogs offshore private military operations:
- **Personnel Recovery**: Ingestion of battlefield recruits via the Fulton Surface-to-Air Recovery System.
- **Combat Deployment**: Authorization of dispatched field operations funded by Gross Military Product (GMP).
- **Medical Platform & Quarantine**: Epidemiological pathogen control during Vocal Cord Parasite outbreaks.

The codebase is built with modern FastAPI and SQLite/SQLAlchemy. While functional, it contains subtle, realistic engineering flaws across the three assessment pillars Jules scans autonomously: **Performance**, **Security & Data Integrity**, and **Design & Architecture**.

---

## Technical Stack

- **Runtime**: Python 3.10+
- **Framework**: FastAPI (ASGI)
- **Database / ORM**: SQLite via SQLAlchemy
- **Data Validation**: Pydantic v2
- **Testing**: Pytest with HTTPX (`pytest-asyncio`)
- **Server**: Uvicorn

---

## Repository Layout

```
.
├── database.py         # SQLite connection engine and session dependency
├── models.py           # SQLAlchemy tables and Pydantic schemas
├── main.py             # FastAPI routes and business logic
├── test_mother_base.py # Pytest test suite (baseline flows + challenge tests)
├── requirements.txt    # Application dependencies
└── README.md           # Operational manual and benchmark briefing
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health and operational status |
| `GET` | `/treasury` | Current Gross Military Product (GMP) balance |
| `GET` | `/staff` | Query staff roster (filter by `unit` and `quarantined`) |
| `POST` | `/fulton/extract` | Recover soldier via Fulton system |
| `POST` | `/dispatch/deploy` | Authorize and deploy combat strike team |
| `POST` | `/quarantine/isolate-outbreak` | Isolate carriers of pathogen vector language |

---

## Quickstart & Local Setup

1. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

4. **Run the test suite**:
   - Run baseline operational tests:
     ```bash
     pytest test_mother_base.py -k "not test_challenge" -v
     ```
   - Run benchmark challenge tests (demonstrating planted flaws):
     ```bash
     pytest test_mother_base.py -k "test_challenge" -v
     ```

---

## Jules Benchmark Evaluation Matrix

Jules autonomously inspects repositories and categorizes suggested patches into three pillars. This application embeds one realistic flaw per pillar:

### 1. Performance Pillar: Fulton Recovery Event Loop Starvation
- **Location**: `POST /fulton/extract` in `main.py`
- **Symptom**: Simulated Fulton uplink latency calls synchronous `time.sleep()` inside an `async def` handler.
- **Impact**: Halts the single-threaded Python ASGI event loop, freezing all concurrent requests (including health checks and telemetry).
- **Target Fix**: Replace synchronous sleep with `await asyncio.sleep()` or delegate blocking operations to worker threads.
- **Test**: `pytest test_mother_base.py -k "test_challenge_performance_event_loop"`

### 2. Security & Data Integrity Pillar: Combat Dispatch TOCTOU Concurrency Race
- **Location**: `POST /dispatch/deploy` in `main.py`
- **Symptom**: Balance check `if treasury.gmp_balance < payload.gmp_cost` and balance deduction are separated across an asynchronous wait point without transaction locks.
- **Impact**: Simultaneous dispatches can double-spend funds, plunging Diamond Dogs into negative GMP debt.
- **Target Fix**: Atomic conditional SQL query (e.g., `UPDATE treasury SET gmp_balance = gmp_balance - :cost WHERE gmp_balance >= :cost`) or transaction-level concurrency control.
- **Test**: `pytest test_mother_base.py -k "test_challenge_security_concurrency_race"`

### 3. Design & Architecture Pillar: Parasite Quarantine Memory Scan & Casing Bug
- **Location**: `POST /quarantine/isolate-outbreak` in `main.py`
- **Symptom**: Loads the entire staff table into Python memory (`db.query(StaffMember).all()`), iterates with an unindexed, case-sensitive substring check (`if target_language in staff.languages`), and calls `db.commit()` on every single matched row.
- **Impact**: O(N) memory allocation, N+1 commit transactions, and silent failure to quarantine soldiers when language casing differs (e.g. `"Kikongo"` vs `"kikongo"`).
- **Target Fix**: SQL-level case-insensitive filtering (`ILIKE` / normalized lookup) and a single bulk update transaction.
- **Test**: `pytest test_mother_base.py -k "test_challenge_design_quarantine_casing"`

---

## Jules & CodeRabbit Workflow

1. Push this repository to a GitHub repository with CodeRabbit installed.
2. Allow Jules to scan the repository autonomously for Security, Performance, and Design enhancements.
3. When Jules proposes a patch, review the generated branch:
   - Run `pytest test_mother_base.py -v` to verify whether the challenge tests transition from RED to GREEN without breaking baseline tests.
   - CodeRabbit will automatically review Jules's pull request diff, checking for side effects, architectural fit, and edge cases.
