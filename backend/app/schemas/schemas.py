from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.models import Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    password: str
    role: Role


class AssetCreate(BaseModel):
    tail_number: str
    model: str


class UsageLogCreate(BaseModel):
    asset_id: int
    flight_hours: float
    source: str = "manual"
    notes: Optional[str] = None


class MaintenanceProgramCreate(BaseModel):
    asset_id: int
    name: str
    interval_hours: Optional[float] = None
    interval_days: Optional[int] = None


class InventoryCreate(BaseModel):
    part_catalog_id: int
    location: str
    on_hand: int = 0
    reserved: int = 0
    min_qty: int = 0
    reorder_point: int = 0
    lead_time_days: int = 7


class MaintenanceDue(BaseModel):
    program_id: int
    due_hours: Optional[float]
    due_date: Optional[datetime]
    overdue: bool
    due_soon: bool
