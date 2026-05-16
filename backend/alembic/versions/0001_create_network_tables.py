"""create network tables

Revision ID: 0001_create_network_tables
Revises:
Create Date: 2026-05-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_create_network_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scans",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("target_name", sa.String(length=200), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_scans_status", "scans", ["status"])

    op.create_table(
        "packet_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("scan_id", sa.String(length=36), sa.ForeignKey("scans.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_ip", sa.String(length=45), nullable=False),
        sa.Column("destination_ip", sa.String(length=45), nullable=False),
        sa.Column("protocol", sa.String(length=20), nullable=False),
        sa.Column("source_port", sa.Integer(), nullable=True),
        sa.Column("destination_port", sa.Integer(), nullable=True),
        sa.Column("packet_size", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_packet_events_scan_id", "packet_events", ["scan_id"])
    op.create_index("ix_packet_events_source_ip", "packet_events", ["source_ip"])
    op.create_index("ix_packet_events_destination_ip", "packet_events", ["destination_ip"])
    op.create_index("ix_packet_events_destination_port", "packet_events", ["destination_port"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("scan_id", sa.String(length=36), sa.ForeignKey("scans.id"), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("rule_name", sa.String(length=100), nullable=False),
        sa.Column("source_ip", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alerts_scan_id", "alerts", ["scan_id"])


def downgrade() -> None:
    op.drop_index("ix_alerts_scan_id", table_name="alerts")
    op.drop_table("alerts")

    op.drop_index("ix_packet_events_destination_port", table_name="packet_events")
    op.drop_index("ix_packet_events_destination_ip", table_name="packet_events")
    op.drop_index("ix_packet_events_source_ip", table_name="packet_events")
    op.drop_index("ix_packet_events_scan_id", table_name="packet_events")
    op.drop_table("packet_events")

    op.drop_index("ix_scans_status", table_name="scans")
    op.drop_table("scans")
