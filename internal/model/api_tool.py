from datetime import datetime
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Index,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    text,
)
from internal.extension.database_extension import db
from sqlalchemy.dialects.postgresql import JSONB


class ApiToolProvider(db.Model):
    __tablename__ = "api_tool_provider"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_api_tool_provider_id"),
        UniqueConstraint(
            "account_id", "name", name="qk_api_tool_provider_account_id_name"
        ),
        Index("idx_api_tool_provider_account_id", "account_id"),
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
    openapi_schema = Column(Text, nullable=False, server_default=text("''::text"))
    headers = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
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


class ApiTool(db.Model):
    __tablename__ = "api_tool"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_api_tool_id"),
        UniqueConstraint(
            "account_id", "provider_id", name="qk_api_tool_account_id_provider_id"
        ),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID, nullable=False)
    provider_id = Column(UUID, nullable=False)
    name = Column(
        String(255), nullable=False, server_default=text("''::character varying")
    )
    description = Column(Text, nullable=False, server_default=text("''::text"))
    url = Column(
        String(255), nullable=False, server_default=text("''::character varying")
    )
    method = Column(
        String(255), nullable=False, server_default=text("''::character varying")
    )
    parameters = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
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

    @property
    def provider(self) -> ApiToolProvider:
        return db.session.query(ApiToolProvider).get(self.provider_id)
