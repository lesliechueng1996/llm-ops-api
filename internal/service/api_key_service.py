"""
@Time   : 2025/01/05 21:58
@Author : Leslie
@File   : api_key_service.py
"""

import secrets
from injector import inject
from dataclasses import dataclass
from internal.model.account import Account
from internal.model.api_key import ApiKey
from internal.schema.api_key_schema import CreateApiKeyReqSchema
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class ApiKeyService:
    db: SQLAlchemy

    def create_api_key(self, req: CreateApiKeyReqSchema, account: Account) -> None:
        api_key = ApiKey(
            account_id=account.id,
            api_key=self.generate_api_key(),
            is_active=req.is_active.data,
            remark=req.remark.data,
        )

        self.db.session.add(api_key)
        self.db.session.commit()

    def generate_api_key(self, api_key_prefix: str = "llmops-v1/") -> str:
        return api_key_prefix + secrets.token_urlsafe(48)
