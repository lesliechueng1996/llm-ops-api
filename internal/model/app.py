"""
@Time   : 2024/12/2 01:06
@Author : Leslie
@File   : app.py
"""

from sqlalchemy import (
    PrimaryKeyConstraint,
    Column,
    UUID,
    String,
    Text,
    DateTime,
    Index,
    text,
)
from uuid import uuid4
from datetime import datetime
from internal.extension.database_extension import db


class App(db.Model):
    """AI应用模型"""

    __tablename__ = "app"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_app_id"),
        Index("idx_app_account_id", "account_id"),
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
    icon = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    description = Column(
        Text, default="", nullable=False, server_default=text("''::text")
    )
    status = Column(
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


class AppDatasetJoin(db.Model):
    __tablename__ = "app_dataset_join"
    __table_args__ = (
        PrimaryKeyConstraint("app_id", "dataset_id", name="pk_app_dataset_join"),
        Index("idx_app_dataset_join_app_id", "app_id"),
        Index("idx_app_dataset_join_dataset_id", "dataset_id"),
    )

    id = Column(
        UUID, default=uuid4, nullable=False, server_default=text("uuid_generate_v4()")
    )
    app_id = Column(UUID, nullable=False)
    dataset_id = Column(UUID, nullable=False)
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
