"""
@Time   : 2025/01/05 21:34
@Author : Leslie
@File   : api_key.py
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Index,
    Boolean,
    PrimaryKeyConstraint,
    String,
    text,
)
from internal.extension.database_extension import db


class ApiKey(db.Model):
    __tablename__ = "api_key"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_api_key_id"),
        Index("idx_api_key_account_id", "account_id"),
    )

    id = Column(
        UUID, default=uuid4, nullable=False, server_default=text("uuid_generate_v4()")
    )
    account_id = Column(UUID, nullable=False)
    api_key = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    is_active = Column(
        Boolean, default=False, nullable=False, server_default=text("false")
    )
    remark = Column(
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


class EndUser(db.Model):
    __tablename__ = "end_user"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_end_user_id"),
        Index("idx_end_user_tenant_id", "tenant_id"),
    )

    id = Column(
        UUID, default=uuid4, nullable=False, server_default=text("uuid_generate_v4()")
    )
    tenant_id = Column(UUID, nullable=False)
    app_id = Column(UUID, nullable=False)
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
