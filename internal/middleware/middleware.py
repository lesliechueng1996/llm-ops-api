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
from internal.service import JWTService, AccountService


@inject
@dataclass
class Middleware:

    jwtService: JWTService
    accountService: AccountService

    def request_loader(self, request: Request) -> Optional[Account]:
        if request.blueprint == "llmops":
            authorization_header = request.headers.get("Authorization")
            if not authorization_header:
                logging.error("Authorization header is missing")
                raise UnauthorizedException("请登录后访问")
            if not authorization_header.startswith("Bearer "):
                logging.error("Authorization header is invalid")
                raise UnauthorizedException("请登录后访问")
            token = authorization_header[7:]

            payload = self.jwtService.decode(token)
            account_id = payload.get("sub")
            account = self.accountService.get_account(account_id)
            return account
        else:
            return None
