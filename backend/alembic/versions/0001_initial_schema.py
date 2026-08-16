"""Create EduSync identity, school, academic and activity tables."""
from alembic import op
from sqlalchemy import text
from app.models import Base

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    bind.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    bind.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    Base.metadata.create_all(bind=bind)

def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
