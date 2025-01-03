"""
@Time   : 2024/12/28 16:57
@Author : Leslie
@File   : account_service.py
"""

import base64
from datetime import datetime, timedelta
import secrets
from uuid import UUID
from flask import request
from injector import inject
from dataclasses import dataclass
from internal.model import Account, AccountOAuth
from internal.service.jwt_service import JWTService
from pkg.sqlalchemy import SQLAlchemy
from pkg.password import hash_password, compare_password
from internal.exception import UnauthorizedException
import logging


@inject
@dataclass
class AccountService:

    db: SQLAlchemy
    jwt_service: JWTService

    def get_account(self, account_id: UUID) -> Account:
        account = self.db.session.query(Account).filter_by(id=account_id).one_or_none()
        return account

    def get_account_oauth_by_provider_name_and_openid(
        self, provider_name: str, openid: str
    ) -> AccountOAuth:
        return (
            self.db.session.query(AccountOAuth)
            .filter_by(provider=provider_name, openid=openid)
            .one_or_none()
        )

    def get_account_by_email(self, email: str) -> Account:
        return self.db.session.query(Account).filter_by(email=email).one_or_none()

    def create_account(self, name: str, email: str) -> Account:
        account = Account(name=name, email=email)
        self.db.session.add(account)
        self.db.session.commit()
        return account

    def update_password(self, account: Account, password: str):
        salt = secrets.token_bytes(16)
        base64_salt = base64.b64encode(salt).decode("utf-8")
        password_hashed = hash_password(password, salt)
        base64_password_hashed = base64.b64encode(password_hashed).decode("utf-8")

        with self.db.auto_commit():
            account.password_salt = base64_salt
            account.password = base64_password_hashed

    def update_name(self, account: Account, name: str):
        with self.db.auto_commit():
            account.name = name

    def update_avatar(self, account: Account, avatar: str):
        with self.db.auto_commit():
            account.avatar = avatar

    def password_login(self, email: str, password: str):
        account = self.get_account_by_email(email)
        if account is None:
            logging.warning(f"account not found, email: {email}")
            raise UnauthorizedException("账号或密码错误")

        if (
            not account.password
            or not account.password_salt
            or not compare_password(password, account.password, account.password_salt)
        ):
            logging.warning(f"password not match, email: {email}")
            raise UnauthorizedException("账号或密码错误")

        expire_at = int((datetime.now() + timedelta(days=30)).timestamp())
        payload = {
            "sub": str(account.id),
            "iss": "llmops",
            "exp": expire_at,
        }
        access_token = self.jwt_service.encode(payload)

        with self.db.auto_commit():
            account.last_login_ip = request.remote_addr
            account.last_login_at = datetime.now()

        return {
            "access_token": access_token,
            "expire_at": expire_at,
        }
