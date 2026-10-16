from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from pydantic import BaseModel, ConfigDict
from database import Base


# SQLAlchemy ORM Models

class Treasury(Base):
    __tablename__ = "treasury"

    id = Column(Integer, primary_key=True, index=True)
    gmp_balance = Column(Integer, nullable=False, default=500000)


class StaffMember(Base):
    __tablename__ = "staff_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codename = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=False)
    rank = Column(String(10), nullable=False)
    languages = Column(String(255), nullable=False)
    is_quarantined = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DispatchMission(Base):
    __tablename__ = "dispatch_missions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    gmp_cost = Column(Integer, nullable=False)
    reward_gmp = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="DEPLOYED")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# Pydantic Schemas (v2)

class TreasuryResponse(BaseModel):
    id: int
    gmp_balance: int

    model_config = ConfigDict(from_attributes=True)


class StaffCreate(BaseModel):
    codename: str
    unit: str
    rank: str
    languages: str


class StaffResponse(BaseModel):
    id: int
    codename: str
    unit: str
    rank: str
    languages: str
    is_quarantined: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DispatchCreate(BaseModel):
    title: str
    gmp_cost: int
    reward_gmp: int


class DispatchResponse(BaseModel):
    id: int
    title: str
    gmp_cost: int
    reward_gmp: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuarantineResponse(BaseModel):
    isolated_count: int
    target_language: str
