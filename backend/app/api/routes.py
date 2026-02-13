from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    require_roles,
)
from app.models.models import (
    Asset,
    AuditAction,
    IndentRequest,
    Inventory,
    MaintenanceProgram,
    PartCatalog,
    PartInstance,
    Role,
    UsageLog,
    User,
    WorkOrder,
    WorkOrderStatus,
)
from app.schemas.schemas import (
    AssetCreate,
    InventoryCreate,
    MaintenanceProgramCreate,
    Token,
    UsageLogCreate,
    UserCreate,
)
from app.services.audit import log_audit
from app.services.inventory import recommended_indent_qty
from app.services.maintenance import evaluate_due

router = APIRouter(prefix="/api")


@router.post("/auth/register", dependencies=[Depends(require_roles(Role.admin))])
def register_user(payload: UserCreate, session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    user = User(username=payload.username, hashed_password=get_password_hash(payload.password), role=payload.role)
    session.add(user)
    session.commit()
    session.refresh(user)
    log_audit(session, "User", str(user.id), AuditAction.create, actor.username, user.model_dump_json())
    session.commit()
    return user


@router.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return Token(access_token=create_access_token(user.username))


@router.post("/assets", dependencies=[Depends(require_roles(Role.admin, Role.maintainer))])
def create_asset(payload: AssetCreate, session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    asset = Asset(**payload.model_dump())
    session.add(asset)
    session.commit()
    session.refresh(asset)
    log_audit(session, "Asset", str(asset.id), AuditAction.create, actor.username, asset.model_dump_json())
    session.commit()
    return asset


@router.get("/assets")
def list_assets(session: Session = Depends(get_session), _: User = Depends(get_current_user)):
    return session.exec(select(Asset)).all()


@router.post("/usage-logs", dependencies=[Depends(require_roles(Role.admin, Role.maintainer))])
def create_usage_log(payload: UsageLogCreate, session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    asset = session.get(Asset, payload.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    usage = UsageLog(**payload.model_dump())
    asset.total_hours += payload.flight_hours
    session.add(usage)
    session.add(asset)
    session.commit()
    session.refresh(usage)
    log_audit(session, "UsageLog", str(usage.id), AuditAction.create, actor.username, usage.model_dump_json())
    session.commit()
    return usage


@router.post("/maintenance-programs", dependencies=[Depends(require_roles(Role.admin, Role.maintainer))])
def create_maintenance_program(payload: MaintenanceProgramCreate, session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    program = MaintenanceProgram(**payload.model_dump())
    session.add(program)
    session.commit()
    session.refresh(program)
    log_audit(session, "MaintenanceProgram", str(program.id), AuditAction.create, actor.username, program.model_dump_json())
    session.commit()
    return program


@router.get("/maintenance/due")
def due_maintenance(session: Session = Depends(get_session), _: User = Depends(get_current_user)):
    programs = session.exec(select(MaintenanceProgram)).all()
    results = []
    for program in programs:
        asset = session.get(Asset, program.asset_id)
        if not asset:
            continue
        due = evaluate_due(program, asset.total_hours)
        if due.due_soon or due.overdue:
            results.append(due)
    return results


@router.post("/work-orders/generate", dependencies=[Depends(require_roles(Role.admin, Role.maintainer))])
def generate_work_orders(session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    programs = session.exec(select(MaintenanceProgram)).all()
    created = []
    for program in programs:
        asset = session.get(Asset, program.asset_id)
        if not asset:
            continue
        due = evaluate_due(program, asset.total_hours)
        if not (due.due_soon or due.overdue):
            continue
        existing = session.exec(
            select(WorkOrder).where(
                WorkOrder.maintenance_program_id == program.id,
                WorkOrder.status != WorkOrderStatus.done,
            )
        ).first()
        if existing:
            continue
        wo = WorkOrder(
            asset_id=program.asset_id,
            maintenance_program_id=program.id,
            due_at_hours=due.due_hours,
            due_at_date=due.due_date,
            is_overdue=due.overdue,
        )
        session.add(wo)
        session.flush()
        log_audit(session, "WorkOrder", str(wo.id), AuditAction.create, actor.username, wo.model_dump_json())
        created.append(wo)
    session.commit()
    return created


@router.post("/parts/catalog", dependencies=[Depends(require_roles(Role.admin, Role.storekeeper))])
def create_part_catalog(payload: dict, session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    part = PartCatalog(**payload)
    session.add(part)
    session.commit()
    session.refresh(part)
    log_audit(session, "PartCatalog", str(part.id), AuditAction.create, actor.username, part.model_dump_json())
    session.commit()
    return part


@router.post("/parts/instances", dependencies=[Depends(require_roles(Role.admin, Role.storekeeper))])
def create_part_instance(payload: dict, session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    instance = PartInstance(**payload)
    session.add(instance)
    session.commit()
    session.refresh(instance)
    log_audit(session, "PartInstance", str(instance.id), AuditAction.create, actor.username, instance.model_dump_json())
    session.commit()
    return instance


@router.post("/parts/instances/{instance_id}/install", dependencies=[Depends(require_roles(Role.admin, Role.maintainer))])
def install_part(instance_id: int, asset_id: int, session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    instance = session.get(PartInstance, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Part instance not found")
    instance.installed_asset_id = asset_id
    instance.installed_at = datetime.utcnow()
    instance.removed_at = None
    session.add(instance)
    session.commit()
    log_audit(session, "PartInstance", str(instance.id), AuditAction.update, actor.username, instance.model_dump_json())
    session.commit()
    return instance


@router.post("/parts/instances/{instance_id}/remove", dependencies=[Depends(require_roles(Role.admin, Role.maintainer))])
def remove_part(instance_id: int, session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    instance = session.get(PartInstance, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Part instance not found")
    instance.removed_at = datetime.utcnow()
    instance.installed_asset_id = None
    session.add(instance)
    session.commit()
    log_audit(session, "PartInstance", str(instance.id), AuditAction.update, actor.username, instance.model_dump_json())
    session.commit()
    return instance


@router.post("/inventory", dependencies=[Depends(require_roles(Role.admin, Role.storekeeper))])
def create_inventory(payload: InventoryCreate, session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    inv = Inventory(**payload.model_dump())
    session.add(inv)
    session.commit()
    session.refresh(inv)
    log_audit(session, "Inventory", str(inv.id), AuditAction.create, actor.username, inv.model_dump_json())
    session.commit()
    return inv


@router.post("/inventory/recommend-indents", dependencies=[Depends(require_roles(Role.admin, Role.storekeeper))])
def recommend_indents(session: Session = Depends(get_session), actor: User = Depends(get_current_user)):
    inventories = session.exec(select(Inventory)).all()
    usage_agg = defaultdict(float)
    for row in session.exec(select(UsageLog)).all():
        usage_agg[row.asset_id] += row.flight_hours
    daily_demand = (sum(usage_agg.values()) / 30.0) if usage_agg else 0.2

    suggestions = []
    for inv in inventories:
        qty = recommended_indent_qty(inv, daily_demand)
        if qty <= 0:
            continue
        indent = IndentRequest(
            part_catalog_id=inv.part_catalog_id,
            location=inv.location,
            suggested_qty=qty,
            reason="Auto-generated due to projected stockout risk",
        )
        session.add(indent)
        session.flush()
        log_audit(session, "IndentRequest", str(indent.id), AuditAction.create, actor.username, indent.model_dump_json())
        suggestions.append(indent)
    session.commit()
    return suggestions


@router.get("/dashboard")
def dashboard(session: Session = Depends(get_session), _: User = Depends(get_current_user)):
    due = due_maintenance(session)
    low_stock = session.exec(select(Inventory).where((Inventory.on_hand - Inventory.reserved) <= Inventory.reorder_point)).all()
    stockout_risk = session.exec(select(IndentRequest).where(IndentRequest.status == "Open")).all()
    return {
        "due_maintenance_count": len(due),
        "low_stock_count": len(low_stock),
        "open_indent_count": len(stockout_risk),
    }


@router.get("/audit-logs", dependencies=[Depends(require_roles(Role.admin))])
def get_audit_logs(session: Session = Depends(get_session), _: User = Depends(get_current_user)):
    from app.models.models import AuditLog

    return session.exec(select(AuditLog).order_by(AuditLog.created_at.desc())).all()
