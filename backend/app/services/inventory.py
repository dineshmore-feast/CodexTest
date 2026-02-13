from math import ceil

from app.models.models import Inventory


def recommended_indent_qty(inventory: Inventory, daily_demand: float, risk_days: int = 30) -> int:
    available = max(inventory.on_hand - inventory.reserved, 0)
    projected_need = ceil(daily_demand * (inventory.lead_time_days + risk_days))
    safety_floor = max(inventory.min_qty, inventory.reorder_point)
    target = max(projected_need, safety_floor)
    return max(target - available, 0)
