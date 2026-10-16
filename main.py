import asyncio
import time
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from database import engine, Base, get_db, SessionLocal
from models import (
    Treasury,
    TreasuryResponse,
    StaffMember,
    StaffResponse,
    StaffCreate,
    DispatchMission,
    DispatchCreate,
    DispatchResponse,
    QuarantineResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        treasury = db.query(Treasury).filter(Treasury.id == 1).first()
        if not treasury:
            treasury = Treasury(id=1, gmp_balance=500000)
            db.add(treasury)
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(
    title="Diamond Dogs Mother Base OS",
    description="Operational command and management API for Mother Base.",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {
        "status": "OPERATIONAL",
        "command": "Diamond Dogs Mother Base",
    }


@app.get("/treasury", response_model=TreasuryResponse)
async def get_treasury(db: Session = Depends(get_db)):
    treasury = db.query(Treasury).filter(Treasury.id == 1).first()
    if not treasury:
        treasury = Treasury(id=1, gmp_balance=500000)
        db.add(treasury)
        db.commit()
        db.refresh(treasury)
    return treasury


@app.get("/staff", response_model=List[StaffResponse])
async def list_staff(
    unit: Optional[str] = Query(None, description="Filter by unit assignment"),
    quarantined: Optional[bool] = Query(None, description="Filter by quarantine status"),
    db: Session = Depends(get_db),
):
    query = db.query(StaffMember)
    if unit:
        query = query.filter(StaffMember.unit == unit)
    if quarantined is not None:
        query = query.filter(StaffMember.is_quarantined == quarantined)
    return query.all()


@app.post("/fulton/extract", response_model=StaffResponse, status_code=201)
async def extract_soldier(payload: StaffCreate, db: Session = Depends(get_db)):
    """
    Recover field personnel via Fulton surface-to-air recovery system.
    Simulates telemetry uplink and chopper pickup before storing personnel record.
    """
    # Telemetry and aerial recovery sync wait (does not block event loop)
    await asyncio.sleep(0.5)

    soldier = StaffMember(
        codename=payload.codename,
        unit=payload.unit,
        rank=payload.rank,
        languages=payload.languages,
        is_quarantined=False,
    )
    db.add(soldier)
    db.commit()
    db.refresh(soldier)
    return soldier


@app.post("/dispatch/deploy", response_model=DispatchResponse, status_code=201)
async def deploy_mission(payload: DispatchCreate, db: Session = Depends(get_db)):
    """
    Deploy combat personnel on external operations.
    Validates and debits operational GMP cost from Mother Base treasury.
    """
    treasury = db.query(Treasury).filter(Treasury.id == 1).first()
    if not treasury or treasury.gmp_balance < payload.gmp_cost:
        raise HTTPException(status_code=400, detail="Insufficient GMP in Mother Base treasury")

    # Processing/network latency between check and deduction (TOCTOU race window)
    await asyncio.sleep(0.05)

    treasury.gmp_balance -= payload.gmp_cost

    mission = DispatchMission(
        title=payload.title,
        gmp_cost=payload.gmp_cost,
        reward_gmp=payload.reward_gmp,
        status="DEPLOYED",
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


@app.post("/quarantine/isolate-outbreak", response_model=QuarantineResponse)
async def isolate_outbreak(
    target_language: str = Query(..., description="Pathogen vector language"),
    db: Session = Depends(get_db),
):
    """
    Scan personnel roster and quarantine carriers of vocal cord parasite vector language.
    """
    # Flaw: In-memory table scan and per-row commits
    all_staff = db.query(StaffMember).all()
    quarantined_count = 0
    for staff in all_staff:
        # Flaw: Case-sensitive substring check
        if target_language in staff.languages:
            staff.is_quarantined = True
            db.commit()
            quarantined_count += 1

    return QuarantineResponse(
        isolated_count=quarantined_count,
        target_language=target_language,
    )



