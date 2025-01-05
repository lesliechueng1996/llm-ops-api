"""
@Time   : 2025/01/05 21:58
@Author : Leslie
@File   : api_key_service.py
"""

import secrets
from uuid import UUID
from injector import inject
from dataclasses import dataclass
from internal.model.account import Account
from internal.model.api_key import ApiKey
from internal.schema.api_key_schema import CreateApiKeyReqSchema
from pkg.sqlalchemy import SQLAlchemy
from internal.exception import NotFoundException


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

    def get_api_key(self, api_key_id: UUID, account: Account) -> ApiKey:
        api_key = (
            self.db.session.query(ApiKey)
            .filter(ApiKey.id == api_key_id, ApiKey.account_id == account.id)
            .one_or_none()
        )

        if not api_key:
            raise NotFoundException("指定的API Key不存在")

        return api_key

    def delete_api_key(self, api_key_id: UUID, account: Account) -> None:
        api_key = self.get_api_key(api_key_id, account)

        self.db.session.delete(api_key)
        self.db.session.commit()

    def update_api_key(
        self, api_key_id: UUID, req: CreateApiKeyReqSchema, account: Account
    ) -> None:
        api_key = self.get_api_key(api_key_id, account)

        with self.db.auto_commit():
            api_key.is_active = req.is_active.data
            api_key.remark = req.remark.data

    def update_api_key_active(
        self, api_key_id: UUID, is_active: bool, account: Account
    ) -> None:
        api_key = self.get_api_key(api_key_id, account)

        with self.db.auto_commit():
            api_key.is_active = is_active

    def generate_api_key(self, api_key_prefix: str = "llmops-v1/") -> str:
        return api_key_prefix + secrets.token_urlsafe(48)
