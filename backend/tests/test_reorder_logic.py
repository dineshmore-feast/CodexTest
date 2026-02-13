from app.models.models import Inventory
from app.services.inventory import recommended_indent_qty


def test_indent_recommendation_positive():
    inv = Inventory(
        id=1,
        part_catalog_id=10,
        location="Main",
        on_hand=5,
        reserved=3,
        min_qty=6,
        reorder_point=8,
        lead_time_days=10,
    )
    qty = recommended_indent_qty(inv, daily_demand=1.2)
    assert qty > 0


def test_indent_recommendation_zero_when_sufficient():
    inv = Inventory(
        id=1,
        part_catalog_id=10,
        location="Main",
        on_hand=100,
        reserved=5,
        min_qty=10,
        reorder_point=20,
        lead_time_days=7,
    )
    qty = recommended_indent_qty(inv, daily_demand=0.5)
    assert qty == 0
