from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session

import time
from database import engine, Base, get_db, SessionLocal
from models import (
    Treasury,
    TreasuryResponse,
    StaffMember,
    StaffResponse,
    StaffCreate,
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
    # Telemetry and aerial recovery sync wait (blocks event loop)
    time.sleep(0.5)

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

