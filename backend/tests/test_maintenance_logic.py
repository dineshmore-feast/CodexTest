from datetime import datetime, timedelta

from app.models.models import MaintenanceProgram
from app.services.maintenance import evaluate_due


def test_due_by_hours_overdue():
    program = MaintenanceProgram(
        id=1,
        asset_id=1,
        name="100h",
        interval_hours=100,
        last_done_hours=20,
        due_soon_buffer_hours=5,
    )
    due = evaluate_due(program, current_hours=121)
    assert due.overdue is True
    assert due.due_soon is True
    assert due.due_hours == 120


def test_due_by_days_due_soon_not_overdue():
    now = datetime.utcnow()
    program = MaintenanceProgram(
        id=2,
        asset_id=1,
        name="Monthly",
        interval_days=30,
        last_done_date=now - timedelta(days=25),
        due_soon_buffer_days=7,
    )
    due = evaluate_due(program, current_hours=0, now=now)
    assert due.overdue is False
    assert due.due_soon is True
