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

    id = Column(UUID, default=uuid4, nullable=False)
    account_id = Column(UUID, nullable=False)
    name = Column(String(255), default="", nullable=False)
    icon = Column(String(255), default="", nullable=False)
    description = Column(Text, default="", nullable=False)
    status = Column(String(255), default="", nullable=False)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    created_at = Column(DateTime, default=datetime.now, nullable=False)
