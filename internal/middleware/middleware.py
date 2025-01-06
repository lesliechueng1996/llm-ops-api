"""
@Time   : 2024/12/28 16:51
@Author : Leslie
@File   : middleware.py
"""

from typing import Optional
from injector import inject
from dataclasses import dataclass
from flask import Request
from internal.exception import UnauthorizedException
from internal.model.account import Account
import logging
from internal.service import JWTService, AccountService, ApiKeyService


@inject
@dataclass
class Middleware:

    jwt_service: JWTService
    account_service: AccountService
    api_key_service: ApiKeyService

    def request_loader(self, request: Request) -> Optional[Account]:
        token = self._validate_header(request)
        if request.blueprint == "llmops":
            payload = self.jwt_service.decode(token)
            account_id = payload.get("sub")

            account = self.account_service.get_account(account_id)
            return account
        elif request.blueprint == "openapi":
            api_key = self.api_key_service.get_api_key_record(token)
            if not api_key or not api_key.is_active:
                raise UnauthorizedException("API Key 无效")
            account_id = api_key.account_id

            account = self.account_service.get_account(account_id)
            return account

        return None

    def _validate_header(self, request: Request):
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            logging.error("Authorization header is missing")
            raise UnauthorizedException("请登录后访问")
        if not authorization_header.startswith("Bearer "):
            logging.error("Authorization header is invalid")
            raise UnauthorizedException("请登录后访问")
        token = authorization_header[7:]

        return token
