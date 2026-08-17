"""Add document OCR storage for databases initialized before the document merge."""
from alembic import op
from sqlalchemy import text
from app.models import Document

revision = "0003_documents_ocr"
down_revision = "0002_timetable_workloads"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute(text("ALTER TYPE document_status ADD VALUE IF NOT EXISTS 'failed'"))
    Document.__table__.create(bind=op.get_bind(), checkfirst=True)

def downgrade() -> None:
    Document.__table__.drop(bind=op.get_bind(), checkfirst=True)
