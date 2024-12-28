"""
@Time   : 2024/12/28 16:57
@Author : Leslie
@File   : account_service.py
"""

from uuid import UUID
from injector import inject
from dataclasses import dataclass
from internal.model.account import Account
from pkg.sqlalchemy import SQLAlchemy


@inject
@dataclass
class AccountService:

    db: SQLAlchemy

    def get_account(self, account_id: UUID) -> Account:
        account = self.db.session.query(Account).filter_by(id=account_id).first()
        return account
