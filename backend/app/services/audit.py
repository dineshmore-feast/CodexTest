from sqlmodel import Session

from app.models.models import AuditAction, AuditLog


def log_audit(session: Session, entity: str, entity_id: str, action: AuditAction, actor: str, payload: str):
    session.add(AuditLog(entity=entity, entity_id=entity_id, action=action, actor=actor, payload=payload))
