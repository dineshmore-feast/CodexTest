from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select

from app.core.db import engine
from app.models.models import Inventory, IndentRequest
from app.services.inventory import recommended_indent_qty


scheduler = BackgroundScheduler()


def auto_indent_job():
    with Session(engine) as session:
        inventories = session.exec(select(Inventory)).all()
        for inv in inventories:
            qty = recommended_indent_qty(inv, daily_demand=0.2)
            if qty > 0:
                session.add(
                    IndentRequest(
                        part_catalog_id=inv.part_catalog_id,
                        location=inv.location,
                        suggested_qty=qty,
                        reason="Scheduled stockout prevention",
                    )
                )
        session.commit()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(auto_indent_job, "interval", hours=6, id="auto-indent", replace_existing=True)
        scheduler.start()
