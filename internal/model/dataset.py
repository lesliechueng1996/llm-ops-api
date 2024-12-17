"""
@Time   : 2024/12/18 00:34
@Author : Leslie
@File   : dataset.py
"""

from datetime import datetime
from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    text,
    Index,
    UniqueConstraint,
)
from internal.extension.database_extension import db
from sqlalchemy.dialects.postgresql import JSONB


class Dataset(db.Model):
    __tablename__ = "dataset"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_dataset_id"),
        Index("idx_dataset_account_id", "account_id"),
        UniqueConstraint("account_id", "name", name="uk_dataset_account_id_name"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)
    name = Column(
        String(255), nullable=False, server_default=text("''::character varying")
    )
    icon = Column(
        String(255), nullable=False, server_default=text("''::character varying")
    )
    description = Column(Text, nullable=False, server_default=text("''::text"))
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


class Document(db.Model):
    __tablename__ = "document"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_document_id"),
        Index("idx_document_account_id", "account_id"),
        Index("idx_document_dataset_id", "dataset_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)
    dataset_id = Column(UUID, nullable=False)
    upload_file_id = Column(UUID, nullable=False)
    process_rule_id = Column(UUID, nullable=False)
    batch = Column(
        String(255), nullable=False, server_default=text("''::character varying")
    )
    name = Column(
        String(255), nullable=False, server_default=text("''::character varying")
    )
    position = Column(Integer, nullable=False, server_default=text("1"))
    character_count = Column(Integer, nullable=False, server_default=text("0"))
    token_count = Column(Integer, nullable=False, server_default=text("0"))
    processing_started_at = Column(DateTime, nullable=True)
    parsing_completed_at = Column(DateTime, nullable=True)
    splitting_completed_at = Column(DateTime, nullable=True)
    indexing_completed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=False, server_default=text("''::text"))
    enabled = Column(Boolean, nullable=False, server_default=text("false"))
    disabled_at = Column(DateTime, nullable=True)
    status = Column(
        String(255), nullable=False, server_default=text("'waiting'::character varying")
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


class Segment(db.Model):
    __tablename__ = "segment"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_segment_id"),
        Index("idx_segment_account_id", "account_id"),
        Index("idx_segment_dataset_id", "dataset_id"),
        Index("idx_segment_document_id", "document_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)
    dataset_id = Column(UUID, nullable=False)
    document_id = Column(UUID, nullable=False)
    node_id = Column(UUID, nullable=False)
    position = Column(Integer, nullable=False, server_default=text("1"))
    content = Column(Text, nullable=False, server_default=text("''::text"))
    character_count = Column(Integer, nullable=False, server_default=text("0"))
    token_count = Column(Integer, nullable=False, server_default=text("0"))
    keywords = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    hash = Column(
        String(255), nullable=False, server_default=text("''::character varying")
    )
    hit_count = Column(Integer, nullable=False, server_default=text("0"))
    enabled = Column(Boolean, nullable=False, server_default=text("false"))
    disabled_at = Column(DateTime, nullable=True)
    processing_started_at = Column(DateTime, nullable=True)
    indexing_completed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=False, server_default=text("''::text"))
    status = Column(
        String(255), nullable=False, server_default=text("'waiting'::character varying")
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


class KeywordTable(db.Model):
    __tablename__ = "keyword_table"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_keyword_table_id"),
        Index("idx_keyword_table_dataset_id", "dataset_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    dataset_id = Column(UUID, nullable=False)
    keyword_table = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
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


class DatasetQuery(db.Model):
    __tablename__ = "dataset_query"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_dataset_query_id"),
        Index("idx_dataset_query_dataset_id", "dataset_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    dataset_id = Column(UUID, nullable=False)
    query = Column(Text, nullable=False, server_default=text("''::text"))
    source = Column(
        String(255), nullable=False, server_default=text("''::character varying")
    )
    source_app_id = Column(UUID, nullable=True)
    created_by = Column(UUID, nullable=False)
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


class ProcessRule(db.Model):
    __tablename__ = "process_rule"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_process_rule_id"),
        Index("idx_process_rule_account_id", "account_id"),
        Index("idx_process_rule_dataset_id", "dataset_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)
    dataset_id = Column(UUID, nullable=False)
    mode = Column(
        String(255), nullable=False, server_default=text("'automic'::character varying")
    )
    rule = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
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
