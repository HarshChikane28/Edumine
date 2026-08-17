"""Merge the attendance and student profile migration branches."""

revision = "0006_merge_heads"
down_revision = ("0004_attendance_nfc", "0005_student_personal_details")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
