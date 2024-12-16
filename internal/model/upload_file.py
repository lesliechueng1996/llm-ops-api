"""
@Time   : 2024/12/17 02:36
@Author : Leslie
@File   : upload_file.py
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    text,
)
from internal.extension.database_extension import db


class UploadFile(db.Model):
    __tablename__ = "upload_file"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_upload_file_id"),
        Index("idx_upload_file_account_id", "account_id"),
    )

    id = Column(
        UUID, default=uuid4, nullable=False, server_default=text("uuid_generate_v4()")
    )
    account_id = Column(UUID, nullable=False)
    name = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    key = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    size = Column(Integer, default=0, nullable=False, server_default=text("0"))
    extension = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    mime_type = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    hash = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
        server_onupdate=text("CURRENT_TIMESTAMP(0)"),
    )
    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
    )
