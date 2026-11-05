"""add database imports table

Revision ID: 4353f4f4a1d9
Revises: 835aab60e49f
Create Date: 2026-07-29 14:52:40.472410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4353f4f4a1d9"
down_revision: Union[str, Sequence[str], None] = "835aab60e49f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ImportStatus enum
    import_status_enum = sa.Enum(
        "pending", "processing", "completed", "failed",
        name="importstatus"
    )
    import_status_enum.create(op.get_bind(), checkfirst=True)

    # Create database_imports table
    op.create_table(
        "database_imports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("status", import_status_enum, nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("imported_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicates_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enriched_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("signals_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_details", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("column_mapping", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_database_imports_user_id", "database_imports", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_database_imports_user_id", "database_imports")
    op.drop_table("database_imports")
    sa.Enum(name="importstatus").drop(op.get_bind(), checkfirst=True)
