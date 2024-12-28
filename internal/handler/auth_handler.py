"""
@Time   : 2024/12/28 22:14
@Author : Leslie
@File   : auth_handler.py
"""

from injector import inject
from dataclasses import dataclass
from flask_login import login_required, logout_user
from internal.schema.auth_schema import (
    PasswordLoginRequestSchema,
    PasswordLoginResponseSchema,
)
from internal.service.account_service import AccountService
from pkg.response import success_message, validate_error_json, success_json


@inject
@dataclass
class AuthHandler:
    account_service: AccountService

    def login(self):
        req = PasswordLoginRequestSchema()
        if not req.validate():
            return validate_error_json(req.errors)
        credentials = self.account_service.password_login(
            req.email.data, req.password.data
        )
        return success_json(PasswordLoginResponseSchema().dump(credentials))

    @login_required
    def logout(self):
        logout_user()
        return success_message("退出登录成功")
