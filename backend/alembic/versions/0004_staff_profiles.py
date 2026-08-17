"""Add optional teacher/admin profile details without changing existing tables."""
from alembic import op
from app.models import StaffProfile

revision = "0004_staff_profiles"
down_revision = "0003_documents_ocr"
branch_labels = None
depends_on = None

def upgrade() -> None:
    StaffProfile.__table__.create(bind=op.get_bind(), checkfirst=True)

def downgrade() -> None:
    # This migration is additive; dropping it is intentionally explicit and never
    # part of normal deployment/rollback workflows.
    StaffProfile.__table__.drop(bind=op.get_bind(), checkfirst=True)
