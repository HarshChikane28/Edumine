"""Add weekly subject workloads and teacher timetable conflict protection."""
from alembic import op
from sqlalchemy import Column, Integer, inspect


revision = "0002_timetable_workloads"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The initial migration uses Base.metadata.create_all(), so a new database
    # may already include these current model fields. Keep this migration safe
    # for both new and existing local databases.
    inspector = inspect(op.get_bind())
    subject_columns = {column["name"] for column in inspector.get_columns("subjects")}
    if "weekly_periods" not in subject_columns:
        op.add_column("subjects", Column("weekly_periods", Integer(), nullable=False, server_default="0"))
        op.alter_column("subjects", "weekly_periods", server_default=None)

    timetable_constraints = inspector.get_unique_constraints("timetable_slots")
    has_teacher_constraint = any(
        set(constraint["column_names"] or []) == {"teacher_id", "day_of_week", "period_number"}
        for constraint in timetable_constraints
    )
    if not has_teacher_constraint:
        op.create_unique_constraint(
            "uq_timetable_slots_teacher_day_period",
            "timetable_slots",
            ["teacher_id", "day_of_week", "period_number"],
        )


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    for constraint in inspector.get_unique_constraints("timetable_slots"):
        if set(constraint["column_names"] or []) == {"teacher_id", "day_of_week", "period_number"}:
            op.drop_constraint(constraint["name"], "timetable_slots", type_="unique")
            break
    if "weekly_periods" in {column["name"] for column in inspector.get_columns("subjects")}:
        op.drop_column("subjects", "weekly_periods")
