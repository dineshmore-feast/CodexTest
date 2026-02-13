from datetime import datetime, timedelta

from app.models.models import MaintenanceProgram
from app.schemas.schemas import MaintenanceDue


def evaluate_due(program: MaintenanceProgram, current_hours: float, now: datetime | None = None) -> MaintenanceDue:
    now = now or datetime.utcnow()

    due_hours = None
    due_date = None
    overdue_hours = False
    overdue_days = False
    due_soon_hours = False
    due_soon_days = False

    if program.interval_hours is not None:
        due_hours = program.last_done_hours + program.interval_hours
        overdue_hours = current_hours >= due_hours
        due_soon_hours = current_hours >= (due_hours - program.due_soon_buffer_hours)

    if program.interval_days is not None:
        due_date = program.last_done_date + timedelta(days=program.interval_days)
        overdue_days = now >= due_date
        due_soon_days = now >= (due_date - timedelta(days=program.due_soon_buffer_days))

    return MaintenanceDue(
        program_id=program.id or 0,
        due_hours=due_hours,
        due_date=due_date,
        overdue=overdue_hours or overdue_days,
        due_soon=due_soon_hours or due_soon_days,
    )
