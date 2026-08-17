"""Add NFC-backed attendance records."""
from alembic import op
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, String, UniqueConstraint, inspect, text
from sqlalchemy.dialects.postgresql import UUID


revision = "0004_attendance_nfc"
down_revision = "0003_documents_ocr"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_enums = {row[0] for row in bind.execute(text("SELECT typname FROM pg_type WHERE typname = 'attendance_status'"))}
    if "attendance_status" not in existing_enums:
        op.execute(text("CREATE TYPE attendance_status AS ENUM ('present', 'absent', 'late')"))

    if "rfid_cards" not in inspector.get_table_names():
        op.create_table(
            "rfid_cards",
            Column("id", UUID(as_uuid=True), primary_key=True),
            Column("uid", String(120), nullable=False),
            Column("student_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            Column("label", String(120), nullable=True),
            Column("is_active", Boolean(), nullable=False, server_default="true"),
            Column("created_at", DateTime(timezone=True), server_default=text("now()"), nullable=False),
        )
        op.create_index("ix_rfid_cards_uid", "rfid_cards", ["uid"], unique=True)

    if "attendance_records" not in inspector.get_table_names():
        op.create_table(
            "attendance_records",
            Column("id", UUID(as_uuid=True), primary_key=True),
            Column("student_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            Column("class_id", UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False),
            Column("attendance_date", Date(), nullable=False),
            Column("status", Enum("present", "absent", "late", name="attendance_status", create_type=False), nullable=False),
            Column("source", String(40), nullable=False, server_default="nfc"),
            Column("scan_uid", String(120), nullable=True),
            Column("scanned_at", DateTime(timezone=True), server_default=text("now()"), nullable=False),
            Column("notes", String(255), nullable=True),
            UniqueConstraint("student_id", "attendance_date", name="uq_attendance_records_student_date"),
        )


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    if "attendance_records" in inspector.get_table_names():
        op.drop_table("attendance_records")
    if "rfid_cards" in inspector.get_table_names():
        op.drop_index("ix_rfid_cards_uid", table_name="rfid_cards")
        op.drop_table("rfid_cards")
    op.execute(text("DROP TYPE IF EXISTS attendance_status"))
