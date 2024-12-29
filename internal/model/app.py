"""
@Time   : 2024/12/2 01:06
@Author : Leslie
@File   : app.py
"""

from sqlalchemy import (
    Integer,
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
from sqlalchemy.dialects.postgresql import JSONB


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
    app_config_id = Column(UUID, nullable=True)
    draft_app_config_id = Column(UUID, nullable=True)
    debug_conversation_id = Column(UUID, nullable=True)
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


class AppConfig(db.Model):
    __tablename__ = "app_config"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_app_config_id"),
        Index("idx_app_config_app_id", "app_id"),
    )

    id = Column(
        UUID, default=uuid4, nullable=False, server_default=text("uuid_generate_v4()")
    )
    app_id = Column(UUID, nullable=False)
    model_config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    dialog_round = Column(Integer, nullable=False, server_default=text("0"))
    preset_prompt = Column(Text, nullable=False, server_default=text("''::text"))
    tools = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    workflows = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    retrieval_config = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    long_term_memory = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    opening_statement = Column(Text, nullable=False, server_default=text("''::text"))
    opening_questions = Column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    speech_to_text = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    text_to_speech = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    review_config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
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


class AppConfigVersion(db.Model):
    __tablename__ = "app_config_version"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_app_config_version_id"),
        Index("idx_app_config_version_app_id", "app_id"),
    )

    id = Column(
        UUID, default=uuid4, nullable=False, server_default=text("uuid_generate_v4()")
    )
    app_id = Column(UUID, nullable=False)
    model_config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    dialog_round = Column(Integer, nullable=False, server_default=text("0"))
    preset_prompt = Column(Text, nullable=False, server_default=text("''::text"))
    tools = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    workflows = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    datasets = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    retrieval_config = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    long_term_memory = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    opening_statement = Column(Text, nullable=False, server_default=text("''::text"))
    opening_questions = Column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    speech_to_text = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    text_to_speech = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    review_config = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    version = Column(Integer, nullable=False, server_default=text("0"))
    config_type = Column(
        String(255), nullable=False, server_default=text("''::character varying")
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
