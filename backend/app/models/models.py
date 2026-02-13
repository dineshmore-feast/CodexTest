from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Role(str, Enum):
    admin = "Admin"
    maintainer = "Maintainer"
    storekeeper = "Storekeeper"
    viewer = "Viewer"


class WorkOrderStatus(str, Enum):
    open = "Open"
    in_progress = "InProgress"
    done = "Done"


class AuditAction(str, Enum):
    create = "CREATE"
    update = "UPDATE"
    delete = "DELETE"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: Role = Field(default=Role.viewer)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Asset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tail_number: str = Field(index=True, unique=True)
    model: str
    status: str = "Active"
    total_hours: float = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UsageLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(index=True, foreign_key="asset.id")
    flight_hours: float
    date: datetime = Field(default_factory=datetime.utcnow)
    source: str = "manual"
    notes: Optional[str] = None


class MaintenanceProgram(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(index=True, foreign_key="asset.id")
    name: str
    interval_hours: Optional[float] = None
    interval_days: Optional[int] = None
    last_done_hours: float = 0
    last_done_date: datetime = Field(default_factory=datetime.utcnow)
    due_soon_buffer_hours: float = 5
    due_soon_buffer_days: int = 7


class WorkOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(index=True, foreign_key="asset.id")
    maintenance_program_id: int = Field(index=True, foreign_key="maintenanceprogram.id")
    due_at_hours: Optional[float] = None
    due_at_date: Optional[datetime] = None
    status: WorkOrderStatus = WorkOrderStatus.open
    is_overdue: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PartCatalog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    part_no: str = Field(index=True, unique=True)
    description: str
    unit: str = "ea"


class PartInstance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    part_catalog_id: int = Field(foreign_key="partcatalog.id", index=True)
    serial_no: Optional[str] = Field(default=None, index=True)
    batch_no: Optional[str] = None
    location: str
    installed_asset_id: Optional[int] = Field(default=None, foreign_key="asset.id")
    installed_at: Optional[datetime] = None
    removed_at: Optional[datetime] = None


class Inventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    part_catalog_id: int = Field(foreign_key="partcatalog.id", index=True)
    location: str = Field(index=True)
    on_hand: int = 0
    reserved: int = 0
    min_qty: int = 0
    reorder_point: int = 0
    lead_time_days: int = 7


class IndentRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    part_catalog_id: int = Field(foreign_key="partcatalog.id", index=True)
    location: str
    suggested_qty: int
    reason: str
    status: str = "Open"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    entity: str
    entity_id: str
    action: AuditAction
    actor: str
    payload: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
