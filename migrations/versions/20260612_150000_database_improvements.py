"""baseline database improvements

Revision ID: 20260612_150000
Revises:
Create Date: 2026-06-12 15:00:00
"""

from alembic import context, op
import sqlalchemy as sa


revision = "20260612_150000"
down_revision = None
branch_labels = None
depends_on = None


def _table_names(bind):
    return set(sa.inspect(bind).get_table_names())


def _column_names(bind, table_name):
    return {column["name"] for column in sa.inspect(bind).get_columns(table_name)}


def _index_names(bind, table_name):
    return {index["name"] for index in sa.inspect(bind).get_indexes(table_name)}


def _create_user_detail():
    op.create_table(
        "user_detail",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_detail_email", "user_detail", ["email"], unique=False)


def _create_uploaded_file():
    op.create_table(
        "uploaded_file",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_data", sa.LargeBinary(), nullable=True),
        sa.Column("storage_path", sa.String(length=500), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("upload_time", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user_detail.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def _ensure_uploaded_file_columns(bind):
    columns = _column_names(bind, "uploaded_file")
    with op.batch_alter_table("uploaded_file") as batch_op:
        if "storage_path" not in columns:
            batch_op.add_column(sa.Column("storage_path", sa.String(length=500), nullable=True))
        if "file_size" not in columns:
            batch_op.add_column(sa.Column("file_size", sa.Integer(), nullable=True))
        if "content_type" not in columns:
            batch_op.add_column(sa.Column("content_type", sa.String(length=120), nullable=True))


def _ensure_uploaded_file_indexes(bind):
    indexes = _index_names(bind, "uploaded_file")
    if "ix_uploaded_file_filename" not in indexes:
        op.create_index("ix_uploaded_file_filename", "uploaded_file", ["filename"], unique=False)
    if "ix_uploaded_file_user_upload_time" not in indexes:
        op.create_index("ix_uploaded_file_user_upload_time", "uploaded_file", ["user_id", "upload_time"], unique=False)
    if "ix_uploaded_file_user_filename" not in indexes:
        op.create_index("ix_uploaded_file_user_filename", "uploaded_file", ["user_id", "filename"], unique=False)


def _create_uploaded_file_indexes():
    op.create_index("ix_uploaded_file_filename", "uploaded_file", ["filename"], unique=False)
    op.create_index("ix_uploaded_file_user_upload_time", "uploaded_file", ["user_id", "upload_time"], unique=False)
    op.create_index("ix_uploaded_file_user_filename", "uploaded_file", ["user_id", "filename"], unique=False)


def upgrade():
    if context.is_offline_mode():
        _create_user_detail()
        _create_uploaded_file()
        _create_uploaded_file_indexes()
        return

    bind = op.get_bind()
    tables = _table_names(bind)

    if "user_detail" not in tables:
        _create_user_detail()
    if "uploaded_file" not in tables:
        _create_uploaded_file()
    else:
        _ensure_uploaded_file_columns(bind)

    _ensure_uploaded_file_indexes(bind)


def downgrade():
    bind = op.get_bind()
    tables = _table_names(bind)

    if "uploaded_file" in tables:
        indexes = _index_names(bind, "uploaded_file")
        for index_name in (
            "ix_uploaded_file_user_filename",
            "ix_uploaded_file_user_upload_time",
            "ix_uploaded_file_filename",
        ):
            if index_name in indexes:
                op.drop_index(index_name, table_name="uploaded_file")

        columns = _column_names(bind, "uploaded_file")
        with op.batch_alter_table("uploaded_file") as batch_op:
            for column_name in ("content_type", "file_size", "storage_path"):
                if column_name in columns:
                    batch_op.drop_column(column_name)

    if "uploaded_file" in tables and "user_detail" in tables:
        op.drop_table("uploaded_file")
        op.drop_table("user_detail")
