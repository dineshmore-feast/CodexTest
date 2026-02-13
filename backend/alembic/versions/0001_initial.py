"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "asset",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tail_number", sa.String(), nullable=False, unique=True),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("total_hours", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "partcatalog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("part_no", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
    )
    op.create_table(
        "usagelog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("asset.id"), nullable=False),
        sa.Column("flight_hours", sa.Float(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
    )
    op.create_table(
        "maintenanceprogram",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("asset.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("interval_hours", sa.Float(), nullable=True),
        sa.Column("interval_days", sa.Integer(), nullable=True),
        sa.Column("last_done_hours", sa.Float(), nullable=False),
        sa.Column("last_done_date", sa.DateTime(), nullable=False),
        sa.Column("due_soon_buffer_hours", sa.Float(), nullable=False),
        sa.Column("due_soon_buffer_days", sa.Integer(), nullable=False),
    )
    op.create_table(
        "workorder",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.Integer(), sa.ForeignKey("asset.id"), nullable=False),
        sa.Column("maintenance_program_id", sa.Integer(), sa.ForeignKey("maintenanceprogram.id"), nullable=False),
        sa.Column("due_at_hours", sa.Float(), nullable=True),
        sa.Column("due_at_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("is_overdue", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "partinstance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("part_catalog_id", sa.Integer(), sa.ForeignKey("partcatalog.id"), nullable=False),
        sa.Column("serial_no", sa.String(), nullable=True),
        sa.Column("batch_no", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("installed_asset_id", sa.Integer(), sa.ForeignKey("asset.id"), nullable=True),
        sa.Column("installed_at", sa.DateTime(), nullable=True),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("part_catalog_id", sa.Integer(), sa.ForeignKey("partcatalog.id"), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("on_hand", sa.Integer(), nullable=False),
        sa.Column("reserved", sa.Integer(), nullable=False),
        sa.Column("min_qty", sa.Integer(), nullable=False),
        sa.Column("reorder_point", sa.Integer(), nullable=False),
        sa.Column("lead_time_days", sa.Integer(), nullable=False),
    )
    op.create_table(
        "indentrequest",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("part_catalog_id", sa.Integer(), sa.ForeignKey("partcatalog.id"), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("suggested_qty", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "auditlog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column("payload", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "auditlog",
        "indentrequest",
        "inventory",
        "partinstance",
        "workorder",
        "maintenanceprogram",
        "usagelog",
        "partcatalog",
        "asset",
        "user",
    ]:
        op.drop_table(table)
