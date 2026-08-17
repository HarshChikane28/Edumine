"""Add nullable personal/contact details to student profiles."""
from alembic import op
from sqlalchemy import Boolean, Column, Date, String
from sqlalchemy.dialects.postgresql import JSONB

revision = "0005_student_personal_details"
down_revision = "0004_staff_profiles"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Existing student rows remain valid because every new field is nullable or
    # has a safe default.
    columns = [
        Column("first_name", String(80), nullable=True), Column("middle_name", String(80), nullable=True), Column("last_name", String(80), nullable=True),
        Column("date_of_birth", Date, nullable=True), Column("gender", String(40), nullable=True), Column("blood_group", String(12), nullable=True),
        Column("marital_status", String(40), nullable=True), Column("nationality", String(80), nullable=True), Column("religion", String(80), nullable=True),
        Column("category", String(80), nullable=True), Column("caste", String(80), nullable=True), Column("sub_caste", String(80), nullable=True),
        Column("mother_tongue", String(80), nullable=True), Column("aadhaar_number", String(40), nullable=True), Column("pan_number", String(20), nullable=True),
        Column("personal_email", String(320), nullable=True), Column("alternate_mobile", String(40), nullable=True), Column("emergency_contact_name", String(160), nullable=True),
        Column("emergency_contact_number", String(40), nullable=True), Column("emergency_contact_relationship", String(80), nullable=True),
        Column("birth_place", String(120), nullable=True), Column("birth_country", String(80), nullable=True), Column("birth_state", String(80), nullable=True), Column("birth_district", String(80), nullable=True),
        Column("native_place", String(120), nullable=True), Column("native_country", String(80), nullable=True), Column("native_state", String(80), nullable=True), Column("native_district", String(80), nullable=True),
        Column("permanent_address", JSONB, nullable=True), Column("current_address", JSONB, nullable=True), Column("permanent_address_same", Boolean, nullable=False, server_default="false"),
    ]
    for column in columns:
        op.add_column("student_profiles", column)

def downgrade() -> None:
    pass
