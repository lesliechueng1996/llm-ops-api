"""
@Time   : 2024/12/28 18:34
@Author : Leslie
@File   : oauth_service.py
"""

from datetime import datetime, timedelta
from injector import inject
from dataclasses import dataclass
from internal.model import AccountOAuth
from internal.service import AccountService, JWTService
from pkg.oauth import GithubOAuth
from os import getenv
from internal.exception import NotFoundException
from pkg.sqlalchemy import SQLAlchemy
from flask import request


@inject
@dataclass
class OAuthService:
    account_service: AccountService
    db: SQLAlchemy
    jwt_service: JWTService

    def get_all_oauth(self):
        github = GithubOAuth(
            client_id=getenv("GITHUB_CLIENT_ID"),
            client_secret=getenv("GITHUB_CLIENT_SECRET"),
            redirect_uri=getenv("GITHUB_REDIRECT_URI"),
        )

        return {"github": github}

    def get_oauth_by_provider_name(self, provider_name: str):
        oauth = self.get_all_oauth().get(provider_name)
        if oauth is None:
            raise NotFoundException(f"该授权方式[{provider_name}]不存在")
        return oauth

    def oauth_login(self, provider_name: str, code: str):
        oauth = self.get_oauth_by_provider_name(provider_name)

        oauth_access_token = oauth.get_access_token(code)

        oauth_user_info = oauth.get_user_info(oauth_access_token)

        account_oauth = (
            self.account_service.get_account_oauth_by_provider_name_and_openid(
                provider_name, oauth_user_info.id
            )
        )
        if account_oauth is None:
            account = self.account_service.get_account_by_email(oauth_user_info.email)
            if account is None:
                account = self.account_service.create_account(
                    name=oauth_user_info.name, email=oauth_user_info.email
                )

            with self.db.auto_commit():
                account_oauth = AccountOAuth(
                    account_id=account.id,
                    provider=provider_name,
                    openid=oauth_user_info.id,
                    encrypted_token=oauth_access_token,
                )
                self.db.session.add(account_oauth)
        else:
            account = self.account_service.get_account(account_oauth.account_id)

        with self.db.auto_commit():
            account.last_login_ip = request.remote_addr
            account.last_login_at = datetime.now()

            account_oauth.encrypted_token = oauth_access_token

        expire_at = int((datetime.now() + timedelta(days=30)).timestamp())
        payload = {
            "sub": str(account.id),
            "iss": "llmops",
            "exp": expire_at,
        }
        access_token = self.jwt_service.encode(payload)

        return {
            "access_token": access_token,
            "expire_at": expire_at,
        }
