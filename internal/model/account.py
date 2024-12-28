"""
@Time   : 2024/12/2 01:06
@Author : Leslie
@File   : account.py
"""

from sqlalchemy import (
    PrimaryKeyConstraint,
    Column,
    UUID,
    String,
    DateTime,
    Index,
    text,
)
from uuid import uuid4
from datetime import datetime
from internal.extension.database_extension import db
from flask_login import UserMixin


class Account(db.Model, UserMixin):
    """用户账户模型"""

    __tablename__ = "account"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_account_id"),
        Index("idx_account_email", "email"),
    )

    id = Column(
        UUID, default=uuid4, nullable=False, server_default=text("uuid_generate_v4()")
    )
    name = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    email = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    password = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    password_salt = Column(
        String(255),
        default=None,
        nullable=True,
    )
    avatar = Column(
        String(255),
        default="",
        nullable=False,
        server_default=text("''::character varying"),
    )
    last_login_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(0)"),
    )
    last_login_ip = Column(
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
